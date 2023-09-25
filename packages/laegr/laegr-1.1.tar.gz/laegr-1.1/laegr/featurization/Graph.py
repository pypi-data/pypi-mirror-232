from typing import Union, Optional


class Graph:
    def __init__(self, nodes: list[list[Union[float, int]]], edge_index: Optional[list[list[int]]],
                 edge_attr: Optional[list[list[float]]], pos: Optional[list[list[float]]],
                 labels: list[list[float]], angles = None
                 ) -> None:
        self.nodes = nodes
        self.edge_index = edge_index
        self.edge_attr = edge_attr
        self.pos = pos
        self.labels = labels
        self.angles = angles
