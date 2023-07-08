import osmnx as ox
import networkx as nx
import geopandas as gpd
import numpy as np
import math
from shapely.geometry import Point
import numpy

default_points = [44254038, 44341323, 670854737, 44448306, 3161262011, 44232104, 44176183, 44532514, 1680069937, 44613980]
default_graph_file_path = "graph/graph_base_case.graphml"
default_num_of_paths = 5
default_neighbourhood_map_file_path = "graph/neighbourhood_map_suburb.geojson"
default_seed = 1000

strategies = {
    1: [1, 5,   1, 0.1, 5, 1, 1, 1, 1, 1, False],
    2: [1, 1, 0.1,   1, 1, 5, 5, 2, 1.7, 1.3, False]
}
# CA=1, OA=1, LP=1, RP=1, OW=1, HS=1, TA=1, TA1=2, TA2=1.7, TA3=1.3


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

        self.graph_OW_False = ox.load_graphml(self.graph_file_path)

        for road_id, (origin_num, destination_num, data) in enumerate(self.graph_OW_False.edges(data=True)):
            # speed limits and length
            if isinstance(data.get('maxspeed'), list):
                base_case = data.get('length') / float(data.get('maxspeed')[0])
            elif isinstance(data.get('maxspeed'), str):
                base_case = data.get('length') / float(data.get('maxspeed'))
            else:
                # if maximum speed is not specified, max speed of 30 km/h is assumed
                # the number of edges without maximum speed is 2402, from the total of 25348 edges (so 9.47%)
                base_case = data.get('length') / 30.0

            nx.set_edge_attributes(self.graph_OW_False,
                                   {(origin_num, destination_num, 0): {
                                       "base_case": base_case},
                                       (origin_num, destination_num, 1): {
                                           "base_case": base_case}})

        self.graph_OW_True = self.graph_OW_False.to_undirected()

        self.graph = self.graph_OW_False
        self.graph_end_strategy = self.graph_OW_False

        # statistic variables
        self.continuity = []
        self.connectivity = []
        self.degree_centrality_means = []
        self.degree_centrality_vars = []
        self.node_frequency = []
        self.path_costs_base_case = {}

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

        self.seed = seed

        np.random.seed(seed)

        points_from_map = []

        percentage_out_of_bound = 0.05
        lat_min = 51.863171
        lat_max = 51.970486
        lon_min = 4.427773
        lon_max = 4.580918

        ten_perc_lat = (lat_max - lat_min) * percentage_out_of_bound
        ten_perc_lon = (lon_max - lon_min) * percentage_out_of_bound

        num_of_points_per_neighbourhood = 1
        for index, row in self.neighbourhood_map.iterrows():
            fit = True
            while fit:
                point = random_points_in_polygon(row["geometry"], num_of_points_per_neighbourhood)[0]
                if (lat_max - ten_perc_lat > point.y > lat_min + ten_perc_lat) & (
                        lon_max - ten_perc_lon > point.x > lon_min + ten_perc_lon):
                    points_from_map.append(point)
                    fit = False

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

        for origin_point in self.points:
            for destination_point in self.points:
                if origin_point == destination_point:
                    continue

                # bereken de base case waardes
                routes = ox.distance.k_shortest_paths(self.graph, origin_point, destination_point, self.num_of_paths,
                                                      weight="base_case")

                path_costs = []
                for route in routes:
                    path_costs.append(len(route))

                self.path_costs_base_case[(origin_point, destination_point)] = sum(path_costs) / len(path_costs)

    def run_model(self, rational=True, CA=1, OA=1, LP=1, RP=1, OW=1, HS=1, TA=1, TA1=2, TA2=1.7, TA3=1.3,
                  num_of_paths=default_num_of_paths,
                  one_way_possible=False, start_strategy=1, end_strategy=2, strategy_change_percentage=1,
                  seed=222, num_of_points_per_neighbourhood=1):
        """
        Function that runs a model scenario
        @param TA: Multiplication factor for traffic avoidance
        @param TA1: Multiplication factor for traffic avoidance
        @param TA2: Multiplication factor for traffic avoidance
        @param TA3: Multiplication factor for traffic avoidance
        @param seed:
        @param num_of_points_per_neighbourhood:
        @param rational: Boolean indicating rational or bounded rational decision making
        @param CA: Multiplication factor for camera avoidance
        @param OA: Multiplication factor for obstacle avoidance
        @param LP: Multiplication factor for lane preference
        @param RP: Multiplication factor for residential preference
        @param OW: Multiplication factor for wrong way preference
        @param HS: Multiplication factor for high speed preference
        @param num_of_paths: number of paths generated per origin-destination pair
        @param one_way_possible: Boolean indicating possibility of driving into a road from the wrong way
        @param start_strategy: Integer number of starting strategy
        @param end_strategy: Integer number of ending strategy
        @param strategy_change_percentage: Float indicating at what time in the run, the strategy changes
        @return: Statistical values of run

        """
        self.reset_scenario_statistics()

        if seed != self.seed:
            self.generate_points(seed, num_of_points_per_neighbourhood)

        print(self.points)
        self.num_of_paths = num_of_paths

        if rational:
            if one_way_possible:
                self.graph = self.graph_OW_True
            else:
                self.graph = self.graph_OW_False

            self.calculate_weights(CA, OA, LP, RP, OW, HS, TA, TA1, TA2, TA3, self.graph)
            self.generate_route_network(rational=True, OA=OA, LP=LP, RP=RP, OW=OW, HS=HS, TA=TA)
            return

        else:
            if strategies[start_strategy][-1]:
                self.graph = self.graph_OW_True
            else:
                self.graph = self.graph_OW_False

            if strategies[end_strategy][-1]:
                self.graph_end_strategy = self.graph_OW_True
            else:
                self.graph_end_strategy = self.graph_OW_False

            self.calculate_weights(*strategies[start_strategy][: -1], self.graph)
            self.calculate_weights(*strategies[end_strategy][: -1], self.graph_end_strategy)

            self.generate_route_network(rational=False, strategy_change_percentage=strategy_change_percentage)

        return self.calculate_scenario_statistics()

    def reset_scenario_statistics(self):
        """
        Function that resets the scenario statistics
        """
        self.continuity = []
        self.connectivity = []
        self.node_frequency = []

    def calculate_scenario_statistics(self):
        """
        Function that calculates the scenario statistics
        @return: the scenario statistics
        """
        node_frequency_mean = sum(self.node_frequency) / len(self.node_frequency)
        node_frequency_var = sum(
            (i - node_frequency_mean) ** 2 for i in self.node_frequency) / len(
            self.node_frequency)

        continuity_mean = sum(self.continuity) / len(self.continuity)
        continuity_vars = sum(
            (i - continuity_mean) ** 2 for i in self.continuity) / len(
            self.continuity)

        connectivity_mean = sum(self.connectivity) / len(self.connectivity)
        connectivity_vars = sum(
            (i - connectivity_mean) ** 2 for i in self.connectivity) / len(
            self.connectivity)

        return {
            "continuity_mean": continuity_mean,
            "continuity_vars": continuity_vars,
            "connectivity_mean": connectivity_mean,
            "connectivity_vars": connectivity_vars,
            'node_frequency_mean': node_frequency_mean,
            'node_frequency_var': node_frequency_var
        }

    def generate_route_network(self, OA=1, LP=1, RP=1, OW=1, HS=1, TA=1, rational=True, strategy_change_percentage=0):
        """
        Function that runs the rational model
        """
        for source in [670854737]:
            routes_in_graph = []
            node_frequency = {}
            total_routes = []
            for sink in self.points:
                continuity_values = []
                # if sink and source are equal, continue to next pair
                if source == sink:
                    continue
                # Calculate top x number of paths between sink and source
                routes = self.calculate_routes(source, sink, rational, strategy_change_percentage)
                # For every route, add the nodes and edges to the route graph
                for route in routes:
                    print(route)
                    total_routes.append(route)
                    # routes_in_graph.append(route)
                    # for i in range(0, len(route) - 1):
                    #
                    #     if i in node_frequency:
                    #         # incrementing the count
                    #         node_frequency[i] += 1
                    #     else:
                    #         # initializing the count
                    #         node_frequency[i] = 1

                    # continuity_values.append(len(route))

                # continuity_values_mean = sum(continuity_values) / len(continuity_values)
                # self.continuity.append(continuity_values_mean / self.path_costs_base_case[(source, sink)])

            #save routes
            # file_path = 'OA' + str(OA) +  'LP' + str(LP) + 'RP' + str(RP) + 'OW' + str(OW) + 'HS' + str(HS) + 'TA' + str(TA) + '.npy'
            # file_path = 'test.npy'
            # numpy.save('notebooks/visualisations/data/' + file_path, np.array(total_routes, dtype=object), allow_pickle=True)
            return

            # calculate relative node frequency
            for node_freq in node_frequency.values():
                self.node_frequency.append(node_freq / self.num_of_paths)

            # Calculate the connectivity of a route by determining the number of routes it intersects with
            for route in routes_in_graph:
                connectivity_route = 0
                for route_it in routes_in_graph:
                    if route == route_it:
                        continue
                    connectivity_route += len(list((value for value in list(route) if value in list(route_it))))
                self.connectivity.append((connectivity_route / len(route)) / self.num_of_paths)

    def calculate_routes(self, source, sink, rational=True, strategy_change_percentage=0, ):
        # Calculate top x number of paths between sink and source
        routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                              weight="used_weight")

        if rational:
            return routes

        adjusted_routes = []
        for route in routes:
            index_to_change = int(len(route) * strategy_change_percentage)
            routes_to_adjust = ox.distance.k_shortest_paths(self.graph_end_strategy, route[index_to_change],
                                                            sink, 1,
                                                            weight="used_weight")

            for route_to_adjust in routes_to_adjust:
                adjusted_routes.append(route[0:index_to_change] + route_to_adjust)

        return adjusted_routes

    def calculate_weights(self, CA, OA, LP, RP, OW, HS, TA, TA1, TA2, TA3, graph):
        """
        Function that calculates the weights of all the edges based on the scenario variables
        @param TA: Multiplication factor for traffic avoidance
        @param TA3: Multiplication factor for traffic avoidance
        @param TA2: Multiplication factor for traffic avoidance
        @param TA1: Multiplication factor for traffic avoidance
        @param CA: Multiplication factor for camera avoidance
        @param OA: Multiplication factor for obstacle avoidance
        @param LP: Multiplication factor for lane preference
        @param RP: Multiplication factor for residential preference
        @param OW: Multiplication factor for wrong way preference
        @param HS: Multiplication factor for high speed preference
        @param graph: the graph that needs to be adapted

        """
        for road_id, (origin_num, destination_num, data) in enumerate(graph.edges(data=True)):

            # speed limits and length
            if isinstance(data.get('maxspeed'), list):
                weight_used = data.get('length') / float(data.get('maxspeed')[0])
                if float(data.get('maxspeed')[0]) > 50:
                    weight_used = weight_used * HS
            elif isinstance(data.get('maxspeed'), str):
                weight_used = data.get('length') / float(data.get('maxspeed'))
                if float(data.get('maxspeed')) > 50:
                    weight_used = weight_used * HS
            else:
                # if maximum speed is not specified, max speed of 30 km/h is assumed
                # the number of edges without maximum speed is 2402, from the total of 25348 edges (so 9.47%)
                weight_used = data.get('length') / 30.0

            # cameras
            if "camera" in data:
                weight_used = weight_used * CA

            # obstacle avoidance
            if "roundabout" in data:
                weight_used = weight_used * OA
            if "traffic_light" in data:
                weight_used = weight_used * OA
            if "bridge" in data:
                weight_used = weight_used * OA
            if "tunnel" in data:
                weight_used = weight_used * OA

            # Lane preference
            if "lanes" in data and int(data["lanes"][0]) > 1:
                weight_used = weight_used * LP

            # residential preference
            if data["highway"] in ['residential']:
                weight_used = weight_used * RP

            # One way
            if data["oneway"]:
                weight_used = weight_used * OW

            # Traffic avoidance
            if 'highway' in data:
                if TA > 1:
                    if data["highway"] in ['motorway', 'motorway_link', 'trunk']:
                        weight_used = weight_used * TA * TA1
                    elif data["highway"] in ['primary', 'primary_link', 'secondary']:
                        weight_used = weight_used * TA * TA2
                    elif data["highway"] in ['tertiary']:
                        weight_used = weight_used * TA * TA3

            nx.set_edge_attributes(graph,
                                   {(origin_num, destination_num, 0): {
                                       "used_weight": weight_used},
                                       (origin_num, destination_num, 1): {
                                           "used_weight": weight_used}})
