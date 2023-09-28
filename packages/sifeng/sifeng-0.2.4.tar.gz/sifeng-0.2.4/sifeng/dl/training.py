import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from typing import Optional, Callable, Tuple

g_device = "cuda:0" if torch.cuda.is_available() else "cpu"

class dl_trainer:
    """A torch model trainer

    Parameters
    ----------
    model: torch.nn.Module
        The model to be trained
    loss: Callable
        The loss function to determine how well the model is
    optimizer:
        The optimizer class
    epoch: int
        The number of epochs
    lr: float
        The learning rate
    patience: float, default `10`
        The patience for earlystop, set to `-1` to disable 
    delta: float, default `0`
        The minimal loss improvement required for the model to be regarded as improving
    verbose: Optional[Callable[[str, float, torch.Tensor, torch.Tensor], None]], default None
        The verbose ouput function for evaluation
    eval_train: bool, default `False`
        Whether to eval the training set as well after training every epoch
    device: torch.device, default `"cuda:0" if torch.cuda.is_available() else "cpu"`
        On which device to train the model
    *args, **kwargs:
        Additional args for optimizer
    """
    def __init__(self,
                 model: nn.Module,
                 loss: nn.Module,
                 optimizer,
                 epoch: int,
                 lr: float,
                 device: torch.device = g_device,
                 verbose: Optional[Callable[[str, int, float, torch.Tensor, torch.Tensor], None]] = None,
                 patience: int = 10,
                 delta: float = 0,
                 eval_train: bool = False,
                 *args, **kwargs) -> None:
        self.device = device
        self.model = model
        self.loss = loss()
        self.epoch = epoch
        self.optimizer = optimizer(self.model.parameters(), lr=lr, *args, **kwargs)
        self.verbose = verbose
        self.patience = patience
        self.delta = delta
        self.eval_train = self.verbose and eval_train

    def train(self,
              train_loader: DataLoader,
              valid_loader: DataLoader
              ) -> None:
        torch.cuda.empty_cache()
        best_loss = np.inf
        patience = self.patience
        self.model.to(self.device)
        for EPOCH in tqdm(range(self.epoch), desc="training", unit="epoch"):
            self.train_epoch(train_loader)
            if self.eval_train:
                train_loss, train_yhat, train_y = self.eval_epoch(train_loader)
                self.verbose("train", EPOCH, train_loss, train_yhat, train_y)
            valid_loss, valid_yhat, valid_y = self.eval_epoch(valid_loader)
            if self.verbose is not None:
                self.verbose("valid", EPOCH, valid_loss, valid_yhat, valid_y)

            patience = patience - 1
            if valid_loss < best_loss - self.delta:
                best_loss = valid_loss
                patience = self.patience
            if patience == 0:
                break

    def predict(self,
                loader: DataLoader
                ) -> Tuple[float, torch.Tensor, torch.Tensor]:
        self.model.eval()
        tot_loss, tot_len = 0, 0
        tot_y, tot_yhat = torch.Tensor(device="cpu"), torch.Tensor(device="cpu")
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(self.device), y.to(self.device)
                yhat = self.model(x)
                loss = self.loss(yhat, y)
                tot_loss = tot_loss + loss.data * y.shape[0]
                tot_len = tot_len + y.shape[0]
                if self.verbose is not None:
                    tot_y = torch.concat([tot_y, y.to("cpu")], dim=0)
                    tot_yhat = torch.concat([tot_yhat, yhat.to("cpu")], dim=0)
        return tot_loss / tot_len, tot_yhat, tot_y
    
    def train_epoch(self,
                    loader: DataLoader
                    ) -> None:
        self.model.train()
        for x, y in loader:
            x, y = x.to(self.device), y.to(self.device)
            yhat = self.model(x)
            loss = self.loss(yhat, y)
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def eval_epoch(self,
                   loader: DataLoader
                   ) -> Tuple[float, torch.Tensor, torch.Tensor]:
        self.model.eval()
        tot_loss, tot_len = 0, 0
        if self.verbose is not None:
            tot_y, tot_yhat = torch.Tensor(device="cpu"), torch.Tensor(device="cpu")
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(self.device), y.to(self.device)
                yhat = self.model(x)
                loss = self.loss(yhat, y)
                tot_loss = tot_loss + loss.data * y.shape[0]
                tot_len = tot_len + y.shape[0]
                if self.verbose is not None:
                    tot_y = torch.concat([tot_y, y.to("cpu")], dim=0)
                    tot_yhat = torch.concat([tot_yhat, yhat.to("cpu")], dim=0)
        if self.verbose is not None:
            return tot_loss / tot_len, tot_yhat, tot_y
        else:
            return tot_loss / tot_len, None, None
