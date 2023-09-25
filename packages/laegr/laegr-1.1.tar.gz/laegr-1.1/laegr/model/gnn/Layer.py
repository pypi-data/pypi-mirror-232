from torch_geometric.nn import NNConv, MessagePassing
from torch_geometric.typing import Adj, OptPairTensor, OptTensor, Size
from typing import Union, Tuple
import torch
from torch_geometric.nn.inits import reset


class NodeCat(MessagePassing):
    def __init__(self, in_channels: int, out_channels: int, nn: torch.nn, aggr: str = "add", num_neighbor: int = 26, **kwargs):
        super().__init__(aggr, **kwargs)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.nn = nn
        self.num_neighbor = num_neighbor

        if isinstance(in_channels, int):
            in_channels = (in_channels, in_channels)
        self.in_channels_l = in_channels[0]
        self.reset_parameters()

    def reset_parameters(self):
        reset(self.nn)
    
    def forward(self, x: Union[torch.Tensor, OptPairTensor], edge_index: Adj, edge_attr: OptTensor = None, size: Size = None) -> torch.Tensor:
        if isinstance(x, torch.Tensor):
            x: OptPairTensor = (x, x)

        # propagate_type: (x: OptPairTensor, edge_attr: OptTensor)
        out = self.propagate(edge_index, x=x, edge_attr=edge_attr, size=size)
        x_r = x[1]
        out = torch.cat((x_r, out), 1)
        return out
    
    def aggregate(self, inputs: torch.Tensor) -> torch.Tensor:
        out = inputs.view(-1, self.num_neighbor*self.out_channels)
        return out
    
    def message(self, x:torch.tensor, edge_attr: torch.Tensor, index: torch.Tensor) -> torch.Tensor:
        x_j = torch.clone(x[1])
        weight = self.nn(edge_attr)
        x_j = x_j[index]
        weight = weight.view(-1, self.in_channels_l, self.out_channels)
        return torch.matmul(x_j.unsqueeze(1), weight).squeeze(1)



class NNConv_Edge_Interaction(NNConv):
    def __init__(self, in_channels: Union[int, Tuple[int, int]], out_channels: int, nn, nn_2, aggr: str = 'add', root_weight: bool = True, bias: bool = True, **kwargs):
        super().__init__(in_channels, out_channels, nn, aggr, root_weight, bias, **kwargs)
        self.nn_2 = nn_2
        
    def message(self, x_j: torch.Tensor, edge_attr: torch.Tensor) -> torch.Tensor:
        weight_1 = self.nn(edge_attr)
        weight_1 = weight_1.view(-1, self.in_channels_l, self.out_channels)
        print(x_j)
        print(x_j.shape)
        print(edge_attr)
        print(edge_attr.shape)
        edge_attr_new = edge_attr.unsqueeze(1)
        edge_attr_new = (edge_attr_new + torch.transpose(edge_attr_new, 0, 1))
        edge_attr_new = edge_attr_new.view(-1, 3)
        print(edge_attr_new.shape)
        weight_2 = self.nn_2(edge_attr_new)
        weight_2 = weight_2.view(-1, self.in_channels_l, self.out_channels)
        x_j_new = x_j.unsqueeze(1)
        x_j_new = (x_j_new + torch.transpose(x_j_new, 0, 1))
        x_j_new = torch.matmul(x_j_new, weight_2)
        x_j_new = torch.sum(x_j_new, dim=0)
        print(x_j_new.shape)
        return torch.matmul(x_j.unsqueeze(1), weight_1).squeeze(1) + x_j_new