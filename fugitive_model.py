import networkx as nx

from pydsol.core.model import DSOLModel
from road_components import Intersection, Road, SourceFugitive, SinkFugitive

import osmnx as ox


class FugitiveModel(DSOLModel):
    """
    Class used to simulate fugitive escape route choice behaviour

    Attributes
    ----------
    simulator:
        PyDSOL core simulator
    filepath: str
        filepath to graph representation to build network

    Methods
    -------
    __init__
        build the initial data set for roads, intersections, sources and sinks. Call the construct_graph() method
    construct_model
        reset model and construct sources
    construct_graph
        call method to construct the intersections and roads based on a provided file
    construct_intersections
        construct intersections
    construct_roads
        construct roads
    """

    def __init__(self, simulator, filepath, fugitive_start, fugitive_end, mental_mode={'camera_avoidance':True}):
        """
        Parameters
        ----------
        simulator: simulator
            the simulator used to run the model
        filepath: str
            the filepath of the graph file used to build the network
        """
        super().__init__(simulator)

        self.fugitive_start = fugitive_start
        self.fugitive_end = fugitive_end

        self.intersections = []
        self.roads = []
        self.sources = []
        self.graph = []
        self.source_fugitive = []
        self.sinks = []
        self.sink_fugitive = []
        self.roads_from_sources = []
        self.roads_to_sinks = []
        self.mental_mode = mental_mode

        self.construct_graph(filepath)

    def construct_model(self):
        """
        Method to reset model and construct sources
        """

        self.reset_model()

        self.construct_sources()
        self.construct_sink()

    def construct_graph(self, filepath):
        """
        Method to construct the intersections and road components of graph

        Parameters
        ----------
        filepath: str
            the filepath of the graph file used to build the network
        """

        graph = ox.load_graphml(filepath)
        self.graph = graph

        # calculate the time that it takes to cross an edge based on the maximum speed and length of an edge
        total = 0
        for road_id, (origin_num, destination_num, data) in enumerate(self.graph.edges(data=True)):
            if isinstance(data.get('maxspeed'),list):
                nx.set_edge_attributes(self.graph,
                                       {(origin_num, destination_num, 0): {
                                           "time_to_cross": data.get('length') / float(data.get('maxspeed')[0])},
                                        (origin_num, destination_num, 1): {
                                            "time_to_cross": data.get('length') / float(data.get('maxspeed')[1])}})

            elif isinstance(data.get('maxspeed'),str):
                nx.set_edge_attributes(self.graph,
                                   {(origin_num, destination_num, 0): {"time_to_cross": data.get('length') / float(data.get('maxspeed'))},
                                    (origin_num, destination_num, 1): {"time_to_cross": data.get('length') / float(data.get('maxspeed'))}})

            else:
                # if maximum speed is not specified, max speed of 30 km/h is assumed
                # the number of edges without maximum speed is 2402, from the total of 25348 edges (so 9.47%)
                # print("origin ", origin_num)
                # print("destination", destination_num)
                total = total + 1
                nx.set_edge_attributes(self.graph,
                                       {(origin_num, destination_num, 0): {
                                           "time_to_cross": data.get('length') / 30.0},
                                        (origin_num, destination_num, 1): {
                                            "time_to_cross": data.get('length') / 30.0}})

        # print("total ", total)

        self.construct_intersections(graph)
        self.construct_roads(graph)

    def construct_intersections(self, graph):
        """
        This method constructs all the intersections from the provided graph

        Parameters
        ----------
        graph: osmnx.graph
            osmnx graph that is used to create the network
        """

        # create an intersection object for all the intersections
        for node, data in graph.nodes(data=True):
            locx = data["x"]
            loxy = data["y"]

            intersection = Intersection(simulator=self.simulator, id=node)

            self.intersections.append(intersection)

    def construct_roads(self, graph):
        """
        This method constructs all roads from the provided graph

        Parameters
        ----------
        graph: osmnx.graph
            osmnx graph that is used to create the network
        """

        # create a road objects for all the roads
        for road_id, (origin_num, destination_num, data) in enumerate(graph.edges(data=True)):
            origin = next((x for x in self.intersections if x.id == origin_num), None)
            destination = next((x for x in self.intersections if x.id == destination_num), None)

            road = Road(simulator=self.simulator,
                        origin=origin,
                        destination=destination,
                        destination_name=destination_num,
                        length=data['length'],
                        data=data,
                        selection_weight=1,
                        road_id=len(self.roads)+1)

            self.roads.append(road)

            # for each road, connect the two components
            if type(origin) == Intersection:
                origin.next.append(self.roads[-1])

    def construct_sources(self):
        """
        Method to construct the sources where the fugitive entity is creates
        """

        self.sources = []
        self.source_fugitive = []

        fugitive_source = SourceFugitive(simulator=self.simulator,
                                         graph = self.graph,
                                         id=self.fugitive_start,
                                         interarrival_time=10000000,
                                         num_entities=1,
                                         fugitive_sink =self.fugitive_end,
                                         fugitive_source=self.fugitive_start,
                                         mental_mode=self.mental_mode
                                         )

        self.sources.append(fugitive_source)
        self.source_fugitive.append(fugitive_source)

        # ADD EDGES FROM SOURCES TO SOURCE LOCATIONS OF LENGTH 0
        origin = fugitive_source
        destination = next((x for x in self.intersections if x.id == self.fugitive_start), None)

        road = Road(simulator=self.simulator,
                    origin=origin,
                    destination=destination,
                    destination_name=self.fugitive_start,
                    length=0.001,
                    selection_weight=1,
                    next=destination,
                    road_id=0
                    )

        fugitive_source.next = road
        self.roads_from_sources.append(road)

    def construct_sink(self):
        """
        Method to construct the sinks where the fugitive entity is deleted
        """

        self.sinks = []
        self.sink_fugitive = []

        fugitive_sink = SinkFugitive(self.simulator, self, 0, name=self.fugitive_end)

        self.sinks.append(fugitive_sink)
        self.sink_fugitive.append(fugitive_sink)

        # ADD EDGES FROM SOURCES TO SOURCE LOCATIONS OF LENGTH 0
        destination = fugitive_sink
        origin = next((x for x in self.intersections if x.id == self.fugitive_end), None)

        road = Road(simulator=self.simulator,
                    origin=origin,
                    destination=destination,
                    destination_name=self.fugitive_end,
                    length=0.001,
                    selection_weight=1,
                    next=destination,
                    road_id=0
                    )

        origin.next = road
        self.roads_to_sinks.append(road)

    @staticmethod
    def reset_model():
        """
        Method to reset model
        """

        classes = [SourceFugitive, Road, Intersection]

    def get_output_statistic(self, entity):
        """
        Method to calculate output statistics and visualize the route taken during simulation
        """
        self.simulator._eventlist.clear()

        node_size = []
        node_color = []
        for node in self.graph.nodes:
            node_size.append(0)
            node_color.append('blue')

        print(entity.output_route.values())

        ox.plot.plot_graph_route(
            self.graph, list(entity.output_route.values()), route_color='b', route_linewidth=4, route_alpha=0.5, orig_dest_size=100, ax=None,
            bgcolor="white", node_color=node_color, node_size=node_size, edge_linewidth=1, edge_color='lightgray'
        )
