import osmnx as ox
import networkx as nx
import geopandas as gpd
import numpy as np
import math

from shapely.geometry import Point

default_points = [44430463, 44465861]
default_graph_file_path = "graph/rotterdam_drive_bbox_cameras_traffic_lights_bridges_roundabouts_tunnels.graphml"
default_num_of_paths = 5
default_neighbourhood_map_file_path = "data/neighbourhood_division/neighbourhood_map.geojson"
default_seed = 1111

strategies = {
    1: [1, 1, 1, 1, 1, 1, 1, 1, True],
    2: [1, 1, 1, 1, 1, 1, 1, 1, True],
    3: [1, 1, 1, 1, 1, 1, 1, 1, False],
    4: [1, 1, 1, 1, 1, 1, 1, 1, False]
}


def random_points_in_polygon(polygon, number):
    points = []
    minx, miny, maxx, maxy = polygon.bounds
    while len(points) < number:
        pnt = Point(np.random.uniform(minx, maxx), np.random.uniform(miny, maxy))
        if polygon.contains(pnt):
            points.append(pnt)
    return points


class route_model:
    """
            Class that contains the code for the criminal fugitive route seeking model.

            Attributes
            ----------
            points:array[int]
                array with the origin and destination points
            graph_file_path:str
                path to file to use for graph
            graph: object

    """

    def __init__(self, points=None, graph_file_path=default_graph_file_path):

        """
            Init method that initializes all the structure of the model.
            This includes loading the graphs and setting the initial values of the necessary statistic variables.
            @param points: origin and destination points
            @param graph_file_path: file path for loading graph

        """
        self.seed = default_seed

        # load the origin and destination points
        if points is None:
            self.points = default_points
        else:
            self.points = points

        self.neighbourhood_map = gpd.read_file(default_neighbourhood_map_file_path)

        self.graph_file_path = graph_file_path
        self.num_of_paths = default_num_of_paths

        self.graph = None
        self.load_graph()

        # save copy of original and undirected graphs
        self.original_graph = self.graph.copy()
        self.undirected_graph = self.graph.copy().to_undirected()

        # graph that is used during the bounded rational model for the second strategy
        self.graph_end_strategy = self.graph.copy()

        # statistic variables
        self.num_nodes = 0
        self.num_edges = 0
        self.continuity = []
        self.connectivity = []
        self.degree_centrality_means = []
        self.degree_centrality_vars = []
        self.betweenness_centrality_means = []
        self.betweenness_centrality_vars = []

    def load_graph(self):
        """
            Function that load the graph
        """
        self.graph = ox.load_graphml(self.graph_file_path)

    def generate_points(self, seed=default_seed, num_of_points_per_neighbourhood=1):
        """
        Function that generates the origin and destination points in the map.
        These are random points based on the neighbourhoods in the map.
        The number of points per neighbourhood is specified which might be multiplied
        if it is one of the large neighbourhoods.
        @param seed:
        @param num_of_points_per_neighbourhood:
        """
        if seed == self.seed:
            return

        np.random.seed(seed)

        points_from_map = []

        for index, row in self.neighbourhood_map.iterrows():
            num_of_points = num_of_points_per_neighbourhood
            if row['name'] == "Centrum":
                num_of_points = num_of_points * 6
            elif row['name'] == "Noord":
                num_of_points = num_of_points * 8
            elif row['name'] == "Kralingen-Crooswijk":
                num_of_points = num_of_points * 5

            # todo checken dat punten >100 meter uit elkaar zijn
            points_from_map = points_from_map + random_points_in_polygon(row["geometry"], num_of_points)

        self.points = []
        for point in points_from_map:
            closest_node = None
            closest_distance = math.inf

            for index1, node in self.graph.nodes(data=True):
                distance = math.dist([point.x, point.y], [node.get("x"), node.get("y")])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_node = index1

            self.points.append(closest_node)

    def run_model(self, rational=True, CA=1, OA=1, LP=1, RP=1, WW=1, HS=1, SR=1, TA=1,
                  num_of_paths=default_num_of_paths,
                  one_way_possible=False, start_strategy=1, end_strategy=1, strategy_change_percentage=1,
                  seed=222, num_of_points_per_neighbourhood=1):
        """
        Function that runs a model scenario
        @param seed:
        @param num_of_points_per_neighbourhood:
        @param rational: Boolean indicating rational or bounded rational decision making
        @param CA: Multiplication factor for camera avoidance
        @param OA: Multiplication factor for obstacle avoidance
        @param LP: Multiplication factor for lane preference
        @param RP: Multiplication factor for residential preference
        @param WW: Multiplication factor for wrong way preference
        @param HS: Multiplication factor for high speed preference
        @param SR: Multiplication factor for short road preference
        @param TA: Multiplication factor for traffic avoidance
        @param num_of_paths: number of paths generated per origin-destination pair
        @param one_way_possible: Boolean indicating possibility of driving into a road from the wrong way
        @param start_strategy: Integer number of starting strategy
        @param end_strategy: Integer number of ending strategy
        @param strategy_change_percentage: Float indicating at what time in the run, the strategy changes
        @return: Statistical values of run
        """
        self.reset_scenario_statistics()
        self.generate_points(seed, num_of_points_per_neighbourhood)

        self.num_of_paths = num_of_paths

        if rational:
            if one_way_possible:
                self.graph = self.undirected_graph.copy()
            else:
                self.graph = self.original_graph.copy()

            self.calculate_weights(CA, OA, LP, RP, WW, HS, SR, TA, self.graph)
            self.run_rational_model()

        else:
            if strategies[start_strategy][-1]:
                self.graph = self.undirected_graph.copy()
            else:
                self.graph = self.original_graph.copy()

            if strategies[end_strategy][-1]:
                self.graph_end_strategy = self.undirected_graph.copy()
            else:
                self.graph_end_strategy = self.original_graph.copy()

            self.calculate_weights(*strategies[start_strategy][: -1], self.graph)
            self.calculate_weights(*strategies[end_strategy][: -1], self.graph_end_strategy)

            self.run_bounded_rational_model(strategy_change_percentage)

        return self.calculate_scenario_statistics()

    def reset_scenario_statistics(self):
        """
        Function that resets the scenario statistics
        """
        self.num_nodes = 0
        self.num_edges = 0
        self.continuity = []
        self.connectivity = []
        self.degree_centrality_means = []
        self.degree_centrality_vars = []
        self.betweenness_centrality_means = []
        self.betweenness_centrality_vars = []

    def calculate_scenario_statistics(self):
        """
        Function that calculates the scenario statistics
        @return: the scenario statistics
        """
        degree_centrality_mean_mean = sum(self.degree_centrality_means) / len(self.degree_centrality_means)

        degree_centrality_var_mean = sum(self.degree_centrality_vars) / len(self.degree_centrality_vars)

        betweenness_centrality_mean_mean = sum(self.betweenness_centrality_means) / len(
            self.betweenness_centrality_means)

        betweenness_centrality_var_mean = sum(self.betweenness_centrality_vars) / len(self.betweenness_centrality_vars)

        continuity_mean = sum(self.continuity) / len(self.continuity)
        continuity_vars = sum(
            (i - continuity_mean) ** 2 for i in self.continuity) / len(
            self.continuity)

        connectivity_mean = sum(self.connectivity) / len(self.connectivity)
        connectivity_vars = sum(
            (i - connectivity_mean) ** 2 for i in self.connectivity) / len(
            self.connectivity)

        return {
            "num_of_nodes": self.num_nodes,
            "num_of_edges": self.num_edges,
            "continuity_mean": continuity_mean,
            "continuity_vars": continuity_vars,
            "connectivity_mean": connectivity_mean,
            "connectivity_vars": connectivity_vars,
            'degree_centrality_mean': degree_centrality_mean_mean,
            'degree_centrality_var': degree_centrality_var_mean,
            'betweenness_centrality_mean': betweenness_centrality_mean_mean,
            'betweenness_centrality_var': betweenness_centrality_var_mean,
        }

    def run_rational_model(self):
        """
        Function that runs the rational model
        """
        counter = 0
        for source in self.points:
            # create empty graph
            route_graph = nx.Graph()
            routes_in_graph = []

            counter2 = 0
            for sink in self.points:
                # if sink and source are equal, continue to next pair
                if source == sink:
                    continue
                # Calculate top x number of paths between sink and source
                if not nx.has_path(self.graph, source, sink):
                    continue
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                      weight="used_weight")  # cpus=1??


                # For every route, add the nodes and edges to the route graph
                for route in routes:
                    routes_in_graph.append(route)
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

                    self.continuity.append(len(route))

            # Calculate the connectivity of a route by determining the number of routes it intersects with
            for route in routes_in_graph:
                connectivity_route = 0
                for route_it in routes_in_graph:
                    if route == route_it:
                        continue
                    if len(list((value for value in route if value in route_it))) > 0:
                        connectivity_route += 1
                self.connectivity.append(connectivity_route)

            self.calculate_OD_statistics(route_graph)

    def run_bounded_rational_model(self, strategy_change_percentage):
        """
        Function that runs the bounded rational model
        @param strategy_change_percentage: Float indicating at what time in the run, the strategy changes
        """
        for source in self.points:
            # create empty graph
            route_graph = nx.Graph()
            routes_in_graph = []

            for sink in self.points:
                # if sink and source are equal, continue to next pair
                if source == sink:
                    continue

                # Calculate top x number of paths between sink and source
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                      weight="used_weight")  # cpus=1??

                # For every route, add the nodes and edges to the route graph
                for route in routes:
                    adjusted_routes = []

                    index_to_change = int(len(route) * strategy_change_percentage)
                    routes_to_adjust = ox.distance.k_shortest_paths(self.graph_end_strategy, route[index_to_change],
                                                                    sink, self.num_of_paths,
                                                                    weight="used_weight")  # cpus=1??

                    for route_to_adjust in routes_to_adjust:
                        adjusted_routes.append(route[0:index_to_change] + route_to_adjust)

                    for adjusted_route in adjusted_routes:
                        routes_in_graph.append(adjusted_route)
                        for i in range(0, len(adjusted_route) - 1):
                            # add nodes
                            if not route_graph.has_node(adjusted_route[i]):
                                route_graph.add_node(adjusted_route[i])

                            if not route_graph.has_node(adjusted_route[i + 1]):
                                route_graph.add_node(adjusted_route[i + 1])

                            # add edges
                            if route_graph.has_edge(adjusted_routes[i], adjusted_routes[i + 1]):
                                nx.set_edge_attributes(route_graph,
                                                       {(adjusted_routes[i], adjusted_routes[i + 1]):
                                                            {"count": route_graph[adjusted_routes[i]][
                                                                          adjusted_routes[i + 1]]['count'] + 1}})
                            else:
                                route_graph.add_edge(adjusted_routes[i], adjusted_routes[i + 1])
                                nx.set_edge_attributes(route_graph,
                                                       {(adjusted_routes[i], adjusted_routes[i + 1]): {"count": 1}})

            # Calculate the connectivity of a route by determining the number of routes it intersects with
            for route in routes_in_graph:
                connectivity_route = 0
                for route_it in routes_in_graph:
                    if route == route_it:
                        continue
                    if len(list((value for value in route if value in route_it))) > 0:
                        connectivity_route += 1
                self.connectivity.append(connectivity_route)

            self.calculate_OD_statistics(route_graph)

    def calculate_weights(self, CA, OA, LP, RP, WW, HS, SR, TA, graph=None):
        """
        Function that calculates the weights of all the edges based on the scenario variables
        @param CA: Multiplication factor for camera avoidance
        @param OA: Multiplication factor for obstacle avoidance
        @param LP: Multiplication factor for lane preference
        @param RP: Multiplication factor for residential preference
        @param WW: Multiplication factor for wrong way preference
        @param HS: Multiplication factor for high speed preference
        @param SR: Multiplication factor for short road preference
        @param TA: Multiplication factor for traffic avoidance
        @param graph: the graph that needs to be adapted
        """
        for road_id, (origin_num, destination_num, data) in enumerate(graph.edges(data=True)):

            # speed limits and length
            if isinstance(data.get('maxspeed'), list):
                weight_used = data.get('length') / float(data.get('maxspeed')[0])

            elif isinstance(data.get('maxspeed'), str):
                weight_used = data.get('length') / float(data.get('maxspeed'))

            else:
                # if maximum speed is not specified, max speed of 30 km/h is assumed
                # the number of edges without maximum speed is 2402, from the total of 25348 edges (so 9.47%)
                weight_used = data.get('length') / 30.0

            # cameras
            if isinstance(data.get("camera"), bool):
                weight_used = weight_used * CA

            # obstacle avoidance
            if isinstance(data.get("tunnel"), bool) or isinstance(data.get("roundabout"), bool) or isinstance(
                    data.get("bridge"), bool) or isinstance(data.get("traffic_light"), bool):
                weight_used = weight_used * OA

            # Lane preference
            if 'lanes' in data and int(data.get('lanes')[0]) > 1:
                weight_used = weight_used * LP

            # residential preference
            if 'highway' in data and data.get('highway') == "residential":
                weight_used = weight_used * RP

            # One way
            if 'oneway' in data and data.get('oneway'):
                weight_used = weight_used * WW

            # High speed preference
            if isinstance(data.get('maxspeed'), list) and float(data.get('maxspeed')[0]) > 50.0:
                weight_used = weight_used * HS

            # Short road preference
            if 'length' in data and data.get('length') > 100:
                weight_used = weight_used * SR

            nx.set_edge_attributes(self.graph,
                                   {(origin_num, destination_num, 0): {
                                       "used_weight": weight_used},
                                       (origin_num, destination_num, 1): {
                                           "used_weight": weight_used}})

            # Traffic avoidance, todo

        # For edge cases in the graph, make sure that each edge has a calculated weight
        for road_id, (origin_num, destination_num, data) in enumerate(self.graph.edges(data=True)):
            if "used_weight" not in data:
                nx.set_edge_attributes(self.graph,
                                       {(origin_num, destination_num, 0): {
                                           "used_weight": data.get("length") / 30.0},
                                           (origin_num, destination_num, 1): {
                                               "used_weight": data.get("length") / 30.0},
                                           (origin_num, destination_num, 2): {
                                               "used_weight": data.get("length") / 30.0},
                                           (origin_num, destination_num, 3): {
                                               "used_weight": data.get("length") / 30.0}})

    def calculate_OD_statistics(self, route_graph):
        """
        Function to calculate the statistics of a origin-destination pair network
        @param route_graph: the route network that is used
        """
        degree_centrality = list(nx.degree_centrality(route_graph).values())
        degree_centrality_mean = sum(degree_centrality) / len(degree_centrality)
        degree_centrality_var = sum((i - degree_centrality_mean) ** 2 for i in degree_centrality) / len(
            degree_centrality)

        betweenness_centrality = list(nx.betweenness_centrality(route_graph).values())
        betweenness_centrality_mean = sum(betweenness_centrality) / len(betweenness_centrality)
        betweenness_centrality_var = sum((i - betweenness_centrality_mean) ** 2 for i in betweenness_centrality) / len(
            betweenness_centrality)

        self.degree_centrality_means.append(degree_centrality_mean)
        self.degree_centrality_vars.append(degree_centrality_var)
        self.betweenness_centrality_means.append(betweenness_centrality_mean)
        self.betweenness_centrality_vars.append(betweenness_centrality_var)

        self.num_nodes = self.num_nodes + route_graph.number_of_nodes()
        self.num_edges = self.num_edges + route_graph.number_of_edges()

    def visualise(self, routes):
        """
        Function to visualize the
        @param routes: the routes to be visualized
        """
        route_pairs = []
        for route in routes:
            for i in range(0, len(route) - 1):
                route_pairs.append((route[i], route[i + 1]))

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
