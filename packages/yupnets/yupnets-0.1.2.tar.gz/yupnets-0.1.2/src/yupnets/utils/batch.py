from typing import Callable, List, Optional, Union

import torch

__all__ = [
    "BatchManager",
]


class BatchManager:
    def __init__(
            self,
            func: Callable,
            batch_size: Optional[int] = None,
    ) -> None:
        self.func = func
        self.batch_size = batch_size

    def __call__(
            self,
            data: torch.Tensor,
    ) -> torch.Tensor:
        if self.batch_size is None:
            return self.func(data)

        else:
            batches = self.split(data)

            res = []

            for batch in batches:
                res.append(self.func(batch))

            res = self.merge(res)

            return res

    def split(
            self,
            data: torch.Tensor,
    ) -> List[torch.Tensor]:
        batches = data.split(self.batch_size, dim=0)

        return batches

    @staticmethod
    def merge(
            batches: List[torch.Tensor],
    ) -> Union[None, torch.Tensor]:
        if list(set(batches)) == [None]:
            return None

        else:
            return torch.cat(batches, dim=0)
