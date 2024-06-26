r"""
The RENOModule is intended for datasets
from the ReNO and CNO papers. Basically,
single input-output datasets
"""

import torch
import torch.nn.functional as F

import lightning as L

from mondrian_lib.metrics import Metrics

class RENOModule(L.LightningModule):
    def __init__(self,
                 model,
                 total_iters,
                 lr=0.001,
                 weight_decay=1e-2):
        super().__init__()
        self.save_hyperparameters()
        self.model = model
        self.total_iters = total_iters
        self.lr = lr
        self.weight_decay = weight_decay
        self.metrics = Metrics(self.log)

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.model.parameters(),
                                      lr=self.lr,
                                      weight_decay=self.weight_decay)
        scheduler = torch.optim.lr_scheduler.OneCycleLR(
                optimizer,
                max_lr=self.lr,
                total_steps=self.total_iters)
        scheduler_config = {'scheduler': scheduler,
                            'interval': 'step'}
        return [optimizer], [scheduler_config]

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        pred = self.model(x)
        loss = self.metrics.log(pred, y, 'Train')
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        pred = self.model(x)
        loss = self.metrics.log(pred, y, 'Val')
        return loss

    def test_step(self, batch, batch_idx):
        x, y = batch
        pred = self.model(x)
        loss = self.metrics.log(pred, y, 'Test')
        return loss
