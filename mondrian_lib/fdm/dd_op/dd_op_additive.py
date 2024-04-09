import torch
import torch.nn as nn
from neuralop.layers.padding import DomainPadding
from neuralop.layers.mlp import MLP
from mondrian_lib.fdm.dd_op.dd_op_base import DDOpBase

class DDOpAdditive(DDOpBase):
    def __init__(
        self,
        layer,
        hc,
        domain_size_x,
        domain_size_y,
        subdomain_size_x,
        subdomain_size_y,
        overlap,
        domain_padding,
        use_coarse_op,
        use_padding
    ):
        super().__init__(layer,
                         hc,
                         domain_size_x,
                         domain_size_y,
                         subdomain_size_x,
                         subdomain_size_y,
                         overlap,
                         domain_padding,
                         use_coarse_op)

        self.padding = DomainPadding(domain_padding)
        self.use_padding = use_padding

    def _apply_op(self, t, x_idx, y_idx, res_per_x, res_per_y):
        h = torch.zeros_like(t)
        mask = torch.zeros_like(t)
        for x in x_idx:
            for y in y_idx:
                h_in = t[:,:,y:y+res_per_y,x:x+res_per_x].clone()
                h_in_pad = self.padding.pad(h_in)
                h_in_pad = self.layer(h_in_pad)
                h_out = self.padding.unpad(h_in_pad)
                h[:,:,y:y+res_per_y,x:x+res_per_x] += h_out
                mask[:,:,y:y+res_per_y,x:x+res_per_x] += 1
        h_damp = h / mask
        return h_damp
