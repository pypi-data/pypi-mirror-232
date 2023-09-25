from typing import Tuple
import torch
from torch_geometric.loader import DataLoader
import numpy as np
from tqdm import tqdm

class TrainingValidation:
    def __init__(self, model: torch.nn.Module, loss_fn = torch.nn.MSELoss(), optimizer=torch.optim.Adam, lr=0.001, epoch=5000) -> None:
        self.model = model
        self.loss_fn = loss_fn
        self.optimizer = optimizer(self.model.parameters(), lr=lr)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.epoch = epoch
    
    def train(self, data: DataLoader, clip=False) -> float:
        losses = []
        for batch in tqdm(data):
            batch.to(self.device)
            self.optimizer.zero_grad()
            # pred = self.model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
            pred = self.model_prediction(batch)
            loss = self.loss_fn(pred, batch.y)
            loss.backward()
            if clip:
                clipping_value = 10 # arbitrary value of your choosing
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), clipping_value)
            self.optimizer.step()
            losses.append(np.sqrt(loss.item()))
        return np.mean(losses), np.max(losses), np.min(losses), np.std(losses)
            
    def validation(self, data: DataLoader) -> Tuple[list[float], list[float], list[float]]:
        y_P, y_T, losses = [], [], []
        with torch.no_grad():
            for batch in tqdm(data):
                batch.to(self.device)
                # pred = self.model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
                pred = self.model_prediction(batch)
                y_P += pred.tolist()
                y_T += batch.y.tolist()
                loss = torch.nn.L1Loss()(batch.y, pred)
                loss = loss.item()
                losses.append(loss)
        return y_T, y_P, np.mean(losses)
    
    def model_prediction(self, batch: DataLoader) -> torch.tensor:
        pred = self.model(batch.x, batch.edge_index, batch.edge_attr)
        return pred
    
    def savingModel(self, path: str) -> None:
        torch.save(self.model.state_dict(), path)


class TrainingValidation_SchNet(TrainingValidation):
    def model_prediction(self, batch: DataLoader) -> torch.tensor:
        # print(batch)
        batch.batch = torch.tensor([i for i in range(len(batch.z))], dtype=torch.long)
        # print(batch.batch)
        batch.to(self.device)
        pred = self.model(batch.z, batch.pos, batch.batch)
        # print(pred)
        return pred


    