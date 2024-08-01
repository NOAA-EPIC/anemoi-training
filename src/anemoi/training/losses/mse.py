import logging
from typing import Optional

import torch
from torch import nn

LOGGER = logging.getLogger(__name__)


class WeightedMSELoss(nn.Module):
    """Latitude-weighted MSE loss."""

    def __init__(
        self,
        node_weights: torch.Tensor,
        data_variances: Optional[torch.Tensor] = None,
        ignore_nans: Optional[bool] = False,
    ) -> None:
        """Latitude- and (inverse-)variance-weighted MSE Loss.

        Parameters
        ----------
        node_weights : torch.Tensor of shape (N, )
            Weight of each node in the loss function
        data_variances : Optional[torch.Tensor], optional
            precomputed, per-variable stepwise variance estimate, by default None
        ignore_nans : bool, optional
            Allow nans in the loss and apply methods ignoring nans for measuring the loss, by default False
        """
        super().__init__()

        self.avg_function = torch.nanmean if ignore_nans else torch.mean
        self.sum_function = torch.nansum if ignore_nans else torch.sum

        self.register_buffer("weights", node_weights, persistent=True)
        if data_variances is not None:
            self.register_buffer("ivar", data_variances, persistent=True)

    def forward(self, pred: torch.Tensor, target: torch.Tensor, squash=True) -> torch.Tensor:
        """Calculates the lat-weighted MSE loss.

        Parameters
        ----------
        pred : torch.Tensor
            Prediction tensor, shape (bs, lat*lon, n_outputs)
        target : torch.Tensor
            Target tensor, shape (bs, lat*lon, n_outputs)
        squash : bool, optional
            Average last dimension, by default True

        Returns
        -------
        torch.Tensor
            Weighted MSE loss
        """
        out = torch.square(pred - target)

        # Use variances if available
        if hasattr(self, "ivar"):
            out *= self.ivar

        # Squash by last dimension
        if squash:
            out = self.avg_function(out, dim=-1)
            # Weight by area
            out = out * self.weights.expand_as(out)
            out /= self.sum_function(self.weights.expand_as(out))
            return self.sum_function(out)

        # Weight by area
        out = out * self.weights[..., None].expand_as(out)
        # keep last dimension (variables) when summing weights
        out /= self.sum_function(self.weights[..., None].expand_as(out), axis=(0, 1, 2))
        return self.sum_function(out, axis=(0, 1, 2))
