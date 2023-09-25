import torch, os, torch_geometric
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GraphConv, SAGEConv, GCNConv, NNConv, CGConv, SchNet
from laegr.model.gnn.Model import Model, Model_GNN_Base, Model_GNN_NN, Model_SchNet
from laegr.model.gnn.Model import Model_GNN_SchNet, Model_GNN_Crystal
from laegr.model.gnn.Layer import NNConv_Edge_Interaction, NodeCat
from laegr.model.gnn.TrainingValidation import TrainingValidation, TrainingValidation_SchNet
import numpy as np
import pandas as pd


class Train:
    def __init__(self, layer_type: str) -> None:
        self.layer_func = self.__determine_layer(layer_type)
        self.layer_type = layer_type

    def build_gnn_model(self, first_layer_size: int, embedding_size: int, layer_number: int) -> torch.nn.Module:
        self.layer_number = layer_number
        self.embedding_size = embedding_size
        gnn_model = Model_GNN_Base(first_layer_size, embedding_size, self.layer_func, layer_number).build_model()
        return gnn_model

    def build_model(self, gnn_model: torch.nn, output_model: torch.nn, activation=torch.nn.ReLU()) -> torch.nn.Module:
        model = Model(gnn_model, output_model, activation)
        return model
    
    def saveModel(self, model: torch.nn, path: str) -> None:
        torch.save(model.state_dict(), path)

    @staticmethod
    def __determine_layer(layer_type: str) -> torch_geometric.nn:
        match layer_type:
            case "GraphConv":
                return GraphConv
            case "SAGEConv":
                return SAGEConv
            case "GCNConv":
                return GCNConv
            case "CGConv":
                return CGConv
            case "NNConv":
                return NNConv
            case "CGConv":
                return CGConv
            case "SchNet":
                return SchNet
            case "NNConv_Edge_Interaction":
                return NNConv_Edge_Interaction
            case "NodeCat":
                return NodeCat
            case _:
                raise Exception(f"Do not support the type: {layer_type}")

    def training(self, model: Model, train_data: DataLoader, validation_data: DataLoader, epoch=100, clip=False,
                 optimizer=torch.optim.Adam, lr=0.001, loss_fn=torch.nn.MSELoss(), output="", early_stop="") -> None:
        Tra_Val = self.create_train_agent(model, epoch, optimizer, loss_fn, lr)
        training_loss, val_loss = [], []
        for cur_epoch in range(epoch):
            cur_train_loss, _, _, _ = Tra_Val.train(train_data, clip)
            _, _, cur_val_loss = Tra_Val.validation(validation_data)
            print(f"current epoch: {cur_epoch}. Training loss is: {cur_train_loss}. Validation loss is: {cur_val_loss}")
            training_loss.append(cur_train_loss)
            val_loss.append(cur_val_loss)
            if (early_stop):
                if (cur_val_loss < early_stop):
                    break
        outputName = self.get_output_name(output)
        pd.DataFrame([training_loss, val_loss]).T.to_csv(f"{outputName}_training_loss.csv")

    def get_output_name(self, output: str) -> str:
        outputName = f"{str(self.layer_type)}_{str(self.layer_number)}_{str(self.embedding_size)}_{output}"
        return outputName

    @staticmethod
    def create_train_agent(model, epoch, optimizer, loss_fn, lr):
        Tra_Val = TrainingValidation(model=model, epoch=epoch, optimizer=optimizer, loss_fn=loss_fn, lr=lr)
        return Tra_Val


class TrainCrystal(Train):
    def __init__(self, layer_type: str) -> None:
        super().__init__(layer_type)

    def build_gnn_model(self, first_layer_size: int, layer_number: int, edge_dim: int) -> torch.nn.Module:
        self.layer_number = layer_number
        self.embedding_size = 1
        gnn_model = Model_GNN_Crystal(first_layer_size, layer_number, edge_dim).build_model()
        return gnn_model


class TrainEdge(Train):
    def __init__(self, layer_type: str) -> None:
        super().__init__(layer_type)

    def build_gnn_model(self, first_layer_size: int, embedding_size: int, layer_number: int,
                        edge_model: torch.nn.Module) -> torch.nn.Module:
        self.layer_number = layer_number
        self.embedding_size = embedding_size
        gnn_model = Model_GNN_NN(first_layer_size, embedding_size, self.layer_func, layer_number,
                                 edge_model).build_model()
        return gnn_model


class TrainSchNet(Train):
    def build_model(self, gnn_model: torch.nn, output_model: torch.nn, activation=torch.nn.ReLU()) -> torch.nn.Module:
        model = Model_SchNet(gnn_model, output_model, activation)
        return model

    def build_gnn_model(self, layer_number: int = 1,
                        hidden_channels: int = 128, num_filters: int = 128, num_interactions: int = 6,
                        num_gaussians: int = 50, cutoff: float = 4.7, max_num_neighbors: int = 26
                        ) -> torch.nn.Module:
        self.layer_number = layer_number
        self.embedding_size = hidden_channels
        self.num_filters = num_filters
        self.num_interactions = num_interactions
        self.num_gaussians = num_gaussians
        gnn_model = Model_GNN_SchNet(layer_number).build_model(hidden_channels, num_filters, num_interactions,
                                                               num_gaussians, cutoff, max_num_neighbors)
        return gnn_model

    def get_output_name(self, output: str) -> str:
        outputName = f"{str(self.layer_type)}_{str(self.layer_number)}_{str(self.embedding_size)}_{self.num_filters}_{self.num_interactions}_{self.num_gaussians}_{output}"
        return outputName

    @staticmethod
    def create_train_agent(model, epoch, optimizer, loss_fn, lr):
        Tra_Val = TrainingValidation_SchNet(model=model, epoch=epoch, optimizer=optimizer, loss_fn=loss_fn, lr=lr)
        return Tra_Val


class TrainEdgeCombine(Train):
    def __init__(self, layer_type: str) -> None:
        super().__init__(layer_type)
