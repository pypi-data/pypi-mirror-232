import torch
from torch_geometric.nn import SchNet, CGConv, global_mean_pool


class Model(torch.nn.Module):
    def __init__(self, gnn_model: torch.nn, output_model: torch.nn, activation: torch.nn.ReLU()) -> None:
        super(Model, self).__init__()
        self.gnn = gnn_model
        self.output = output_model
        self.activation = activation

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        for idx in range(len(self.gnn)-1):
            x = self.gnn[idx](x, edge_index, edge_attr)
            x = self.activation(x)
        x = self.gnn[-1](x, edge_index, edge_attr)
        out = self.output(x)
        return out
    # def forward(self, x: torch.Tensor, edge_index: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
    #     for idx in range(len(self.gnn)):
    #         x = self.gnn[idx](x, edge_index, edge_attr)
    #         x = self.activation(x)
    #     # x = self.gnn[-1](x, edge_index, edge_attr)
    #     out = self.output(x)
    #     return out


class Model_SchNet(Model):
    def forward(self, x: torch.Tensor, pos: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
        for idx in range(len(self.gnn)-1):
            x = self.gnn[idx](x, pos, batch)
            x = self.activation(x)
        x = self.gnn[-1](x, pos, batch)
        out = self.output(x)
        return out


class Model_GNN_Base():
    def __init__(self, first_layer_size: int, embedding_size: int, layer_type: torch.nn, layer_number: int) -> None:
        self.embedding_size = embedding_size
        self.layer_type = layer_type
        self.layer_number = layer_number
        self.first_layer_size = first_layer_size

    def build_model(self) -> torch.nn.ModuleList:
        model = torch.nn.ModuleList()
        for idx in range(self.layer_number):
            if (idx == 0):
                cur_layer = self.define_layer(self.first_layer_size)
            else:
                cur_layer = self.define_layer(self.embedding_size)
            model.append(cur_layer)
        return model

    def define_layer(self, input_size: int):
        return self.layer_type(input_size, self.embedding_size)



class Model_GNN_Crystal():
    def __init__(self, first_layer_size: int, layer_number: int, edge_dim: int) -> None:
        self.layer_number = layer_number
        self.first_layer_size = first_layer_size
        self.edge_dim = edge_dim

    def build_model(self) -> torch.nn.ModuleList:
        model = torch.nn.ModuleList()
        for _ in range(self.layer_number):
            cur_layer = CGConv(self.first_layer_size, dim=self.edge_dim)
            model.append(cur_layer)
        return model
        


class Model_GNN_SchNet():
    def __init__(self, layer_number: int = 1) -> None:
        self.layer_number = layer_number

    def build_model(self,   hidden_channels: int = 128, num_filters: int = 128, num_interactions: int = 6, 
                            num_gaussians: int = 50,    cutoff: float = 4.7,   max_num_neighbors: int = 26
                    ) -> torch.nn.ModuleList:
        model = torch.nn.ModuleList()
        for _ in range(self.layer_number):
            cur_layer = SchNet(hidden_channels=hidden_channels, num_filters=num_filters, num_interactions=num_interactions,
                                num_gaussians=num_gaussians, cutoff=cutoff, max_num_neighbors=max_num_neighbors)
            model.append(cur_layer)
        return model

    # def define_layer(self):
    #     return self.layer_type()


class Model_GNN_NN(Model_GNN_Base):
    def __init__(self, first_layer_size: int, embedding_size: int, layer_type: torch.nn, layer_number: int, edge_model_list: torch.nn) -> None:
        super().__init__(first_layer_size, embedding_size, layer_type, layer_number)
        self.edge_model_list = edge_model_list
    
    def build_model(self) -> torch.nn.ModuleList:
        model = torch.nn.ModuleList()
        for idx in range(self.layer_number):
            if (idx == 0):
                cur_layer = self.define_layer(self.first_layer_size, idx)
            else:
                cur_layer = self.define_layer(self.embedding_size, idx)
            model.append(cur_layer)
        return model
    
    def define_layer(self, input_size: int, idx: int):
        return self.layer_type(input_size, self.embedding_size, self.edge_model_list[idx])



        

