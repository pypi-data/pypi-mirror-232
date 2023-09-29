import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader
from tqdm.auto import tqdm

from typing import Optional, Callable, Tuple, Union

g_device = "cuda:0" if torch.cuda.is_available() else "cpu"

class dl_trainer:
    """A torch model trainer

    Parameters
    ----------
    model: torch.nn.Module
        The model to be trained
    loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor]
        The loss function to determine how well the model is
    optimizer: torch.optim.Optimizer
        The optimizer class
    epoch: int
        The number of epochs
    lr: float
        The learning rate
    mini_batch: int, default `1`
        Mini-batch training, accumulates multiple losses before back propagating. Useful for small GPU memory.
    lr_scheduler: Optional[Callable[[int], float]], default `None`
        A function which computes a multiplicative factor given an integer parameter epoch, `None` to disable
    bs_scheduler: Optional[Callable[[int], float]], default `None`
        A function which computes a multiplicative factor given an integer parameter epoch, `None` to disable
    patience: float, default `10`
        The patience for earlystop, set to `-1` to disable 
    delta: float, default `0`
        The minimal loss improvement required for the model to be regarded as improving
    override: Optional[Callable[[int, float, torch.Tensor, torch.Tensor], float]], default `None`
        The override function, that, if returns better metric for a eval epoch, forces patience to reset
    verbose: Optional[Callable[[str, float, torch.Tensor, torch.Tensor], None]], default `None`
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
                 loss: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
                 optimizer: torch.optim.Optimizer,
                 epoch: int,
                 lr: float,
                 mini_batch: int = 1,
                 lr_scheduler: Optional[Callable[[int], float]] = None,
                 bs_scheduler: Optional[Callable[[int], float]] = None,
                 device: torch.device = g_device,
                 verbose: Optional[Callable[[str, int, float, torch.Tensor, torch.Tensor], None]] = None,
                 patience: int = 10,
                 delta: float = 0,
                 override: Optional[Callable[[int, float, torch.Tensor, torch.Tensor], float]] = None,
                 eval_train: bool = False,
                 *args, **kwargs) -> None:
        self.device = device
        self.model = model
        self.loss = loss
        self.epoch = epoch
        self.mini_batch = mini_batch
        self.optimizer = optimizer(self.model.parameters(), lr=lr, *args, **kwargs)
        self.lr_scheduler = torch.optim.lr_scheduler.LambdaLR(self.optimizer, lr_lambda=lr_scheduler) if lr_scheduler is not None else None
        self.bs_scheduler = bs_scheduler
        self.verbose = verbose
        self.patience = patience
        self.delta = delta
        self.override = override if self.patience != -1 else None
        self.eval_train = self.verbose is not None and eval_train

        self.save_result = self.verbose is not None or self.override is not None

    def train(self,
              train_loader: DataLoader,
              valid_loader: DataLoader
              ) -> None:
        torch.cuda.empty_cache()
        best_loss = np.inf
        if self.override is not None:
            best_metric = None
        patience = self.patience
        self.model.to(self.device)
        for EPOCH in tqdm(range(self.epoch), desc="training", unit="epoch"):
            self.train_epoch(EPOCH, train_loader)
            if self.eval_train:
                train_loss, train_yhat, train_y = self.eval_epoch(train_loader)
                self.verbose("train", EPOCH, train_loss.to("cpu"), train_yhat, train_y)
            valid_loss, valid_yhat, valid_y = self.eval_epoch(valid_loader)
            if self.verbose is not None:
                self.verbose("valid", EPOCH, valid_loss.to("cpu"), valid_yhat, valid_y)

            patience = patience - 1
            if self.override is not None:
                valid_metric = self.override(EPOCH, valid_loss.to("cpu"), valid_yhat, valid_y)
                if best_metric < valid_metric:
                    best_metric = valid_metric
                    patience = self.patience
            if valid_loss < best_loss - self.delta:
                best_loss = valid_loss
                patience = self.patience
            if patience == 0:
                break
        
            if self.scheduler is not None:
                self.scheduler.step()

    def predict(self,
                input,
                ):
        self.model.eval()
        with torch.no_grad():
            if isinstance(input, DataLoader):
                tot_loss, tot_len = 0, 0
                tot_y, tot_yhat = torch.Tensor(device="cpu"), torch.Tensor(device="cpu")
                for x, y in input:
                    x, y = x.to(self.device), y.to(self.device)
                    yhat = self.model(x)
                    loss = self.loss(yhat, y)
                    tot_loss = tot_loss + loss.data * y.shape[0]
                    tot_len = tot_len + y.shape[0]
                    tot_y = torch.concat([tot_y, y.to("cpu")], dim=0)
                    tot_yhat = torch.concat([tot_yhat, yhat.to("cpu")], dim=0)
                    return tot_loss / tot_len, tot_yhat, tot_y
            elif isinstance(input, torch.Tensor):
                input = input.to(self.device)
                yhat = self.model(input)
                return yhat.to("cpu")
    
    def train_epoch(self,
                    epoch: int,
                    loader: DataLoader
                    ) -> None:
        if self.bs_scheduler is not None:
            mini_batch = self.mini_batch * self.bs_scheduler(epoch)
        else:
            mini_batch = self.mini_batch
        mini_batch_countr = 0
        self.model.train()
        for x, y in loader:
            x, y = x.to(self.device), y.to(self.device)
            yhat = self.model(x)
            loss = self.loss(yhat, y) / mini_batch
            if mini_batch_countr == 0:
                self.optimizer.zero_grad()
            loss.backward()
            mini_batch_countr = mini_batch_countr + 1
            if mini_batch_countr == mini_batch:
                self.optimizer.step()
                mini_batch_countr = 0
        if mini_batch_countr != 0:
            self.optimizer.step()

    def eval_epoch(self,
                   loader: DataLoader
                   ) -> Tuple[float, torch.Tensor, torch.Tensor]:
        self.model.eval()
        tot_loss, tot_len = 0, 0
        if self.save_result is not None:
            tot_y, tot_yhat = torch.Tensor(device="cpu"), torch.Tensor(device="cpu")
        with torch.no_grad():
            for x, y in loader:
                x, y = x.to(self.device), y.to(self.device)
                yhat = self.model(x)
                loss = self.loss(yhat, y)
                tot_loss = tot_loss + loss.data * y.shape[0]
                tot_len = tot_len + y.shape[0]
                if self.save_result is not None:
                    tot_y = torch.concat([tot_y, y.to("cpu")], dim=0)
                    tot_yhat = torch.concat([tot_yhat, yhat.to("cpu")], dim=0)
        if self.save_result is not None:
            return tot_loss / tot_len, tot_yhat, tot_y
        else:
            return tot_loss / tot_len, None, None
