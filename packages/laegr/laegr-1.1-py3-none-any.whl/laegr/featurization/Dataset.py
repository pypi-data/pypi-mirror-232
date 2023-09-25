from torch_geometric.data.data import Data
import torch
import ovito.data
from typing import Union, Optional

from laegr.featurization.Graph import Graph
from laegr.featurization.GraphFeatures import AtomicMassDistance, AtomicMass3D, AtomicNumberDistance, AtomicNumberPos
from laegr.featurization.GraphFeatures import OnehotDistance, Onehot3D


class GNNData:
    def __init__(self, source: Union[str, ovito.data.DataCollection], criteria: Union[int, float], feature: str,
                 label: Optional[list[list[float]]] = None) -> None:
        self.data = source
        self.label = label
        self.criteria = criteria
        self.feature = feature

    def toData(self) -> Data:
        graph = self.toGraph()
        data = self.toPytorchGNNData(graph)
        return data

    def toGraph(self) -> Graph:
        match self.feature:
            case "AtomicMassDistance":
                graph = AtomicMassDistance(self.data, self.label).toGraph(self.criteria)
            case "AtomicMass3D":
                graph = AtomicMass3D(self.data, self.label).toGraph(self.criteria)
            case "AtomicNumberDistance":
                graph = AtomicNumberDistance(self.data, self.label).toGraph(self.criteria)
            case "AtomicNumberPos":
                graph = AtomicNumberPos(self.data, self.label).toGraph(self.criteria)
            case "OnehotDistance":
                graph = OnehotDistance(self.data, self.label).toGraph(self.criteria)
            case "Onehot3D":
                graph = Onehot3D(self.data, self.label).toGraph(self.criteria)
            case _:
                raise Exception('''Only support six different features:   
                                        AtomicMassDistance,             AtomicMass3D,
                                        AtomicNumberDistance,           AtomicNumberPos,
                                        OnehotDistance,                 Onehot3D.''')
        return graph

    @staticmethod
    def toPytorchGNNData(graph: Graph) -> Data:
        labels = graph.labels
        if graph.labels:
            labels = torch.tensor(graph.labels, dtype=torch.float)
        if graph.pos:
            nodes = torch.tensor(graph.nodes, dtype=torch.long)
            edge_index = torch.tensor(graph.edge_index, dtype=torch.long)
            edge_pos = torch.tensor(graph.pos, dtype=torch.float)
            edge_attr = torch.tensor(graph.edge_attr, dtype=torch.float)
            angles = torch.tensor(graph.angles, dtype=torch.float)
            data = Data(z=nodes, edge_index=edge_index.t().contiguous(), edge_attr=edge_attr, pos=edge_pos, y=labels, angels=angles)
        else:
            nodes = torch.tensor(graph.nodes, dtype=torch.float)
            edge_index = torch.tensor(graph.edge_index, dtype=torch.long)
            edge_attr = torch.tensor(graph.edge_attr, dtype=torch.float)
            data = Data(x=nodes, edge_index=edge_index.t().contiguous(), edge_attr=edge_attr, y=labels)
        return data
