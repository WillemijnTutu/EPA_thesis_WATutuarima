import networkx as nx
import itertools
import math
import osmnx as ox

from pydsol.model.entities import Entity


class Fugitive(Entity):
    """
    Class used to simulate a fugitive entity

    Attributes
    ----------
    simulator:
        PyDSOL core simulator
    t:int
        time_creations
    speed:int
        The speed of the fugitive in m/min
    name:str
        The assigned name of the fugitive entity
    id_iter_fug:int
        Integer representation of fugitive id
    route_planned:array[int]
        The list of currently planned nodes to follow along the route
    output_route:array[int]
        The list of nodes that have been moved through
    graph: osmnx.graph
        graph that represents the network
    fugitive_source:int
        The starting location of the fugitive entity
    fugitive_sink:int
        The goal location of the fugitive entity
    camera_avoidance:Bool
        A boolean representing whether the fugitive is avoiding cameras

    Methods
    -------
    __init__
        Method to initialise the fugitive entity
    set_route
        Method to set the route of a fugitive
    set_camera_avoidance
        Method to incorporate camera avoidance into routing decisions
    """

    id_iter_fug = itertools.count(1)

    def __init__(self, simulator, t, mode, graph, fugitive_sink, fugitive_source, **kwargs):
        """
        Method to initialise fugitive entity

        Parameters
        ----------
        simulator:
            PyDSOL core simulator
        t:int
            time_creations
        mode:array[Bool]
            array representing the mental mode of the fugitive
            camera_avoidance:Bool
                A boolean representing whether the fugitive is avoiding cameras
        graph: osmnx.graph
            graph that represents the network
        fugitive_source:int
            The starting location of the fugitive entity
        fugitive_sink:int
            The goal location of the fugitive entity
        kwargs:
            the keyword arguments that are used to expand the entity class
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
        """
        Method to set the route of a fugitive

        This is currently done using a shortest path algorithm based on the time to cross of road components
        """

        self.route_planned = ox.distance.shortest_path(self.graph, self.fugitive_source, self.fugitive_sink,
                                                       weight='time_to_cross', cpus=1)
        print(self.route_planned)

    def set_camera_avoidance(self):
        """
        Method to incorporate camera avoidance into routing decisions
        """

        for (u, v, data) in self.graph.edges(data=True):
            if 'camera' in data:
                nx.set_edge_attributes(self.graph,
                                       {(u, v, 0): {"time_to_cross": math.inf},
                                        (u, v, 1): {"time_to_cross": math.inf}})
