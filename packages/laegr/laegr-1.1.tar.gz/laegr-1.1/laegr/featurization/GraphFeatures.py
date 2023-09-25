from laegr.featurization.Graph import Graph
from ovito.io import import_file
from ovito.data import NearestNeighborFinder, CutoffNeighborFinder
from typing import Union, Any, Optional
import ovito.data
from abc import ABC, abstractmethod
import math
import numpy as np

class GetGraph(ABC):
    """
    Base class to generate the Graph (node features, edges and labels/PE)
    """
    def __init__(self, data: Union[str, ovito.data.DataCollection],
                 labels: Optional[list[list[float]]]) -> None:
        self.labels = labels
        if isinstance(data, str):
            # assert labels is None, "The labels should be None if the input data is lammps file."
            pipeline = import_file(data)
            self.data = pipeline.compute()
        else:
            self.data = data
            # self.labels = labels

    @abstractmethod
    def getNodeFeatures(self) -> list[list[Union[float, int]]]:
        pass

    def getLabels(self) -> list[list[float]]:
        if self.labels:
            return self.labels
        labels = self.data.particles['c_eng'][...]
        labels = [[i] for i in labels]
        return labels


class GraphFeatures(GetGraph):
    def __init__(self, data: Union[str, ovito.data.DataCollection],
                 labels: Optional[list[list[float]]]) -> None:
        super().__init__(data, labels)

    def toGraph(self, criteria: Union[int, float]) -> Graph:
        nodes = self.getNodeFeatures()
        edge_index, edge_attr = self.getEdge(criteria)
        labels = self.getLabels()
        graph_features = Graph(nodes, edge_index, edge_attr, None, labels)
        return graph_features

    def getNodeFeatures(self) -> list[list[Union[float, int]]]:
        raise NotImplementedError

    def getEdge(self, criteria: Union[int, float]) -> tuple[list[list[int | Any]], list[list[float]]]:
        self.finder = None
        if isinstance(criteria, int):
            self.finder = NearestNeighborFinder(criteria, self.data)
        if isinstance(criteria, float):
            self.finder = CutoffNeighborFinder(criteria, self.data)
        assert self.finder is not None, "The criteria to find neighbor should be int or float."
        edge_index = []
        edge_attr = []
        for index in range(self.data.particles.count):
            for neigh in self.finder.find(index):
                edge_index.append([index, neigh.index])
                edge_attr.append(self.getEdgeAttribute(neigh))
        return edge_index, edge_attr

    @staticmethod
    @abstractmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder) -> list[float]:
        pass


class AtomicNumber(GraphFeatures):
    def getNodeFeatures(self) -> list[list[int]]:
        ptypes = self.data.particles.particle_types
        nodes = []
        transform = {1: 42, 2: 41, 3: 73, 4: 74}
        for atom_type in ptypes:
            cur_node = transform[atom_type]
            nodes.append(cur_node)
        return nodes

    @staticmethod
    @abstractmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        pass



class AtomicNumberDistance(AtomicNumber):
    @staticmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        return [neigh.distance]



class AtomicNumberPos(AtomicNumberDistance):
    def toGraph(self, criteria) -> Graph:
        nodes = self.getNodeFeatures()
        edge_index, edge_attr = self.getEdge(criteria)
        pos = self.getPosition()
        labels = self.getLabels()
        angles = self.getAngle()
        graph_features = Graph(nodes, edge_index, edge_attr, pos, labels, angles)
        return graph_features
    

    def getPosition(self) -> list[list[float]]:
        pos_list = []
        for cur_pos in self.data.particles.positions:
            pos_list.append(list(cur_pos))
        return pos_list
    
    def getAngle(self) -> list[float]:
        angles = []
        for index in range(self.data.particles.count):
            cur_distance = []
            for neigh in self.finder.find(index):
                cur_distance.append(neigh.delta)
            for idx_1 in range(len(cur_distance)):
                for idx_2 in range(len(cur_distance)):
                    if idx_1 == idx_2:
                        continue
                    cur_angle = self.__calcAnge(cur_distance[idx_1], cur_distance[idx_2])
                    angles.append(cur_angle)
        return angles
    
    @staticmethod
    def __calcAnge(x: list[float], y: list[float]) -> float:
        dot_product = np.dot(x, y)
        m_x = np.linalg.norm(x)
        m_y = np.linalg.norm(y)
        val = dot_product / (m_x * m_y)
        if val < -1:
            val = -1
        if val > 1:
            val = 1
        angle = math.acos(val)
        return angle

class AtomicMass(GraphFeatures):
    def getNodeFeatures(self) -> list[list[float]]:
        nodes = self.data.particles['Mass'][...]
        nodes = [[i] for i in nodes]
        return nodes

    @staticmethod
    @abstractmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        pass



class AtomicMassDistance(AtomicMass):
    @staticmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        return [neigh.distance]



class AtomicMass3D(AtomicMass):
    @staticmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        return list(neigh.delta)



class OnehotGraph(GraphFeatures):
    def getNodeFeatures(self) -> list[list[int]]:
        ptypes = self.data.particles.particle_types
        nodes = []
        for atom_type in ptypes:
            cur_node = self.toOneHot(atom_type)
            nodes.append(cur_node)
        return nodes

    @staticmethod
    def toOneHot(atom_type: int) -> list[int]:
        if atom_type == 1:
            new_atom_type = 2
        elif atom_type == 2:
            new_atom_type = 1
        else:
            new_atom_type = atom_type
        feature = [0, 0, 0, 0]
        feature[new_atom_type - 1] = 1
        return feature

    @staticmethod
    @abstractmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        pass



class OnehotDistance(OnehotGraph):
    @staticmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        return [neigh.distance]



class Onehot3D(OnehotGraph):
    @staticmethod
    def getEdgeAttribute(neigh: NearestNeighborFinder.Neighbor) -> list[float]:
        return list(neigh.delta)





