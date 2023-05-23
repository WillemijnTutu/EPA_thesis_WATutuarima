# import fugitive_model
# import logging
#
# from pydsol.core.simulator import DEVSSimulatorFloat
# from pydsol.core.experiment import SingleReplication
# from pydsol.model.basic_logger import get_module_logger
import osmnx as ox
import networkx as nx

class RunModel:
    default_start_points = [44430463]
    default_destination_points = [44465861]
    default_graph_file_path = "graph/rotterdam_drive_with_cameras_on_edges.graphml"
    default_num_of_paths = 5

    def __init__(self, start_points=default_start_points, destination_points=default_destination_points,
                 graph_file_path=default_graph_file_path, num_of_paths=default_num_of_paths):

        self.start_points = start_points
        self.destination_points = destination_points
        self.graph_file_path = graph_file_path
        self.num_of_paths = num_of_paths
        # load graph

        self.graph = None
        self.load_graph()

        simulator = None
        model = None

    def load_graph(self):

        self.graph = ox.load_graphml(self.graph_file_path)

    def run_replication(self, mode='default'):

        if mode.startswith('rational'):
            self.run_rational_model(mode.removeprefix('rational_'))
        else:
            self.run_bounded_rational_model(mode)

    def run_rational_model(self, mode):
        for source in self.start_points:
            # create empty graph
            route_graph = nx.Graph()
            for sink in self.destination_points:
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                     weight=mode)  # cpus=1??

                for route in routes:
                    for i in range(0, len(route) - 1):
                        # add nodes
                        if not route_graph.has_node(route[i]):
                            route_graph.add_node(route[i])

                        if not route_graph.has_node(route[i + 1]):
                            route_graph.add_node(route[i + 1])

                        # add edges
                        if route_graph.has_edge(route[i], route[i + 1]):
                            nx.set_edge_attributes(route_graph,
                                                   {(route[i], route[i + 1]):
                                                        {"count": route_graph[route[i]][route[i + 1]]['count'] + 1}})
                        else:
                            route_graph.add_edge(route[i], route[i + 1])
                            nx.set_edge_attributes(route_graph, {(route[i], route[i + 1]): {"count": 1}})

                        # self.visualise(routes)
            # save graph

            file_path = "results/rational_" + mode + ".graphml"
            nx.write_graphml_lxml(route_graph, file_path)

            # add statistics in excel

    def visualise(self, routes):

        route_pairs = []
        for route in routes:
            for i in range(0, len(route) - 1):
                route_pairs.append((route[i], route[i+1]))

        node_size = []
        node_color = []
        for node in self.graph.nodes:
            node_size.append(0)
            node_color.append('blue')

        edge_color = []
        for road_id, (origin_num, destination_num, data) in enumerate(self.graph.edges(data=True)):
            if (origin_num, destination_num) in route_pairs:
                edge_color.append("red")
            else:
                edge_color.append("grey")

        ox.plot.plot_graph(
            self.graph, bgcolor="white", node_color=node_color, node_size=node_size, edge_linewidth=1,
            edge_color=edge_color
        )

    def run_bounded_rational_model(self, mode):
        return

        # simulator = DEVSSimulatorFloat("sim")
        #
        # model = fugitive_model.FugitiveModel(simulator, filepath, fugitive_start, fugitive_end)
        #
        # replication = SingleReplication("rep1", 0.0, 0.0, 15)
        # simulator.initialize(model, replication)
        # simulator.start()
