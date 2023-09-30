from typing import Callable, Dict, Optional

import torch

__all__ = [
    "FeatureExtractor",
]


class FeatureExtractor(torch.nn.Module):
    def __init__(
            self,
            model: torch.nn.Module,
            batch_size: Optional[int] = None,
            use_cuda: bool = False,
    ) -> None:
        from .utils import get_layer_ids, get_layer
        super().__init__()

        self.model = model
        self.batch_size = batch_size
        self.use_cuda = use_cuda
        self.machine = "cuda" if use_cuda else "cpu"

        layer_ids = get_layer_ids(model)
        self.features = dict()

        self.hooks = []

        for layer_id in layer_ids:
            layer = get_layer(model, layer_id)
            layer_kind = layer.__class__.__name__

            self.hooks.append(
                layer.register_forward_hook(self.save_outputs_hook(layer_id, layer_kind))
            )

    def save_outputs_hook(
            self,
            layer_id: str,
            layer_kind: str,
    ) -> Callable:
        def fn(_, __, output):
            layer_key = f"{len(self.features)}-{layer_kind}-{layer_id}"

            if isinstance(output, tuple):
                output = [out for out in output if out is not None]
                output = torch.cat(output, dim=0)

            if layer_key in self.features.keys():
                self.features[layer_key] = torch.cat([
                    self.features[layer_key], output.detach().cpu(),
                ], dim=0)

            else:
                self.features[layer_key] = output.detach().cpu()

        return fn

    def forward(
            self,
            x: torch.Tensor,
    ) -> Dict[str, torch.Tensor]:
        def func(x):
            _ = self.model(x.to(self.machine))

        from ..utils import BatchManager

        batch_manager = BatchManager(func, self.batch_size)
        batch_manager(x)

        for hook in self.hooks:
            hook.remove()

        return self.features
