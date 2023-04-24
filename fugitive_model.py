from pydsol.core.model import DSOLModel
from road_components import Intersection, Road, SourceFugitive

import osmnx as ox

class FugitiveModel(DSOLModel):
    """
    Class used to simulate fugitive escape route choice behaviour

    Attributes
    ----------
    simulator:
        PyDSOL core simulator

    Methods
    -------



    """

    def __init__(self, simulator):
        super().__init__(simulator)

        self.fugitive_start = 44871340
        self.fugitive_end = 1584013959

        self.intersections = []
        self.roads = []
        self.sources = []
        self.graph = []
        self.source_fugitive = []
        self.roads_from_sources = []

        self.construct_graph()

    def construct_model(self):

        self.reset_model()

        self.construct_sources(self.graph)

    def construct_graph(self):

        filepath = "graph/delft_drive.graphml"
        graph = ox.load_graphml(filepath)

        self.graph = graph
        self.construct_intersections(graph)
        self.construct_roads(graph)

    """
    This method constructs all the intersections from the provided graph
    """
    def construct_intersections(self, graph):

        #create a intersection object for all the intersections
        for node, data in graph.nodes(data=True):
            locx = data["x"]
            loxy = data["y"]

            intersection = Intersection(simulator=self.simulator, id=node)

            self.intersections.append(intersection)

    """
    This method constructs all roads from the provided graph
    """
    def construct_roads(self, graph):

        #create a road objects for all the roads
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

            #for each road, connect the two components
            if type(origin) == Intersection:
                origin.next.append(self.roads[-1])

    def construct_sources(self, graph):
        self.sources = []
        self.source_fugitive = []

        fugitive_source = SourceFugitive(simulator=self.simulator,
                                         graph = self.graph,
                                         id=self.fugitive_start,
                                         interarrival_time=10000000,
                                         num_entities=1,
                                         fugitive_sink =self.fugitive_end
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

    @staticmethod
    def reset_model():
        classes = [SourceFugitive, Road, Intersection]

    def get_output_statistic(self):
        self.simulator._eventlist.clear()

        list_fugitives = []
        for source in self.source_fugitive:
            list_fugitives.append(source.entities_created)
            del source

        for fugitive in list_fugitives:
            node_size = []
            node_color = []
            for node in self.graph.nodes:
                node_size.append(0)
                node_color.append('blue')

            ox.plot.plot_graph_route(
                self.graph, list(fugitive.output_route.values()), route_color='b', route_linewidth=4, route_alpha=0.5, orig_dest_size=100, ax=None,
                bgcolor="white", node_color=node_color, node_size=node_size, edge_linewidth=1, edge_color='lightgray'
            )

            print(fugitive.output_route.values())





