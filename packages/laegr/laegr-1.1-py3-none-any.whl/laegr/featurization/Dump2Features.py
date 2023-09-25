from typing import Union, Optional
from ovito.io import import_file
import pandas as pd


class Graph:
    def __init__(self, nodes: list[list[Union[float, int]]], edge_index: Optional[list[list[int]]],
                 edge_attr: Optional[list[list[float]]], pos: Optional[list[list[float]]],
                 labels: list[list[float]]
                 ) -> None:
        self.nodes = nodes
        self.edge_index = edge_index
        self.edge_attr = edge_attr
        self.pos = pos
        self.labels = labels


class Dump2Features:
    """
    Base class to generate the Graph/Matrix (node features, edges and labels/PE) of the given dump file
    The dump file should contain the information of atomic mass and atomic potential energy
    """

    def __init__(self, file_path: str) -> None:
        pipeline = import_file(file_path)
        self.data = pipeline.compute()

    def __toDataFrame(self) -> pd:
        df = pd.DataFrame([self.data.particles.identifiers, self.data.particles.particle_types,
                           self.data.particles['Mass'][...], self.data.particles['c_eng'][...]]).T
        df.columns = ["id", 'type', 'mass', 'c_eng']
        return df

    def get_node_features(self) -> NotImplemented:
        raise NotImplementedError

    def get_labels(self) -> list[list[float]]:
        labels = self.data.particles['c_eng'][...]
        labels = [[i] for i in labels]
        return labels
