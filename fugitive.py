import networkx as nx
from pydsol.model.entities import Entity
import itertools
import math

import osmnx as ox


class Fugitive(Entity):
    """
    Class used to simulate a fugitive entity

    Parameters
    ----------
    simulator:
        PyDSOL core simulator
    t:int
        time_creations
    kwargs:
        the keyword arguments that are used to expand the entity class
    """

    id_iter_fug = itertools.count(1)

    def __init__(self, simulator, t, mode, graph, fugitive_sink, fugitive_source, **kwargs):
        """
        Method to initialise fugitive entity
        """

        self.speed = 500
        # 30 km/h is 500 m per minuut
        super().__init__(simulator, t, self.speed, **kwargs)

        self.name = f"{self.__class__.__name__} {str(next(self.id_iter_fug))}"
        self.route_planned = []

        self.output_route = {}

        self.graph = graph
        self.fugitive_sink = fugitive_sink
        self.fugitive_source = fugitive_source

        self.camera_avoidance = mode['camera_avoidance']

        if self.camera_avoidance:
            self.set_camera_avoidance()

        self.set_route()

    def set_route(self):
        self.route_planned = ox.distance.shortest_path(self.graph, self.fugitive_source, self.fugitive_sink, weight='time_to_cross', cpus=1)

    def set_camera_avoidance(self):

        # for roads that lead up to an intersection, make the time to cross very high (inf)
        for index1, node in self.graph.nodes(data=True):
            if node.get("camera"):
                for road_id, (origin_num, destination_num, data) in self.graph.edges(node):
                    nx.set_edge_attributes(self.graph,
                                           {(origin_num, destination_num, 0): {
                                               "time_to_cross": math.inf},
                                               (origin_num, destination_num, 1): {"time_to_cross": math.inf}})

