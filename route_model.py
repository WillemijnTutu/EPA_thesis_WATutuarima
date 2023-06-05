import osmnx as ox
import networkx as nx

default_points = [44430463, 44465861]
default_graph_file_path = "graph/rotterdam_drive_with_cameras_on_edges.graphml"
default_num_of_paths = 5

strategies = {
    1: [1, 1, 1, 1, 1, 1, 1, 1, True],
    2: [1, 1, 1, 1, 1, 1, 1, 1, True],
    3: [1, 1, 1, 1, 1, 1, 1, 1, False],
    4: [1, 1, 1, 1, 1, 1, 1, 1, False]
}


class route_model:

    def __init__(self, points=None,
                 graph_file_path=default_graph_file_path, num_of_paths=default_num_of_paths, graph=None
                 ):
        if points is None:
            self.points = default_points
        else:
            self.points = points

        self.graph_file_path = graph_file_path
        self.num_of_paths = num_of_paths
        # load graph

        self.graph = graph
        if graph is None:
            self.graph = self.load_graph()

        self.original_graph = self.graph.copy()
        self.undirected_graph = self.graph.copy().to_undirected()

        self.graph_end_strategy = self.graph.copy()

        self.num_nodes = 0
        self.num_edges = 0
        self.continuity = []
        self.connectivity = []
        self.degree_centrality_means = []
        self.degree_centrality_vars = []
        self.betweenness_centrality_means = []
        self.betweenness_centrality_vars = []

    def load_graph(self):
        return ox.load_graphml(self.graph_file_path)

    def run_model(self, rational=True, CA=1, OA=1, LP=1, RP=1, WW=1, HS=1, SR=1, TA=1,
                  num_of_paths=default_num_of_paths,
                  one_way_possible=False, start_strategy=1, end_strategy=1, strategy_change_percentage=1):

        self.reset_scenario_statistics()

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
        self.num_nodes = 0
        self.num_edges = 0
        self.continuity = []
        self.connectivity = []
        self.degree_centrality_means = []
        self.degree_centrality_vars = []
        self.betweenness_centrality_means = []
        self.betweenness_centrality_vars = []

    def calculate_scenario_statistics(self):
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
            "num_of_nodes" : self.num_nodes,
            "num_of_edges" : self.num_edges,
            "continuity_mean" : continuity_mean,
            "continuity_vars" : continuity_vars,
            "connectivity_mean" : connectivity_mean,
            "connectivity_vars" : connectivity_vars,
            'degree_centrality_mean': degree_centrality_mean_mean,
            'degree_centrality_var': degree_centrality_var_mean,
            'betweenness_centrality_mean': betweenness_centrality_mean_mean,
            'betweenness_centrality_var': betweenness_centrality_var_mean,
        }

    def run_rational_model(self):

        for source in self.points:
            # create empty graph
            route_graph = nx.Graph()
            routes_in_graph = []
            for sink in self.points:
                if source == sink:
                    continue
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                      weight="used_weight")  # cpus=1??

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

        for source in self.points:
            # create empty graph
            route_graph = nx.Graph()
            routes_in_graph = []
            for sink in self.points:
                if source == sink:
                    continue
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                      weight="used_weight")  # cpus=1??

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
        for road_id, (origin_num, destination_num, data) in enumerate(graph.edges(data=True)):
            # speed limits and length
            weight_used = 0

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

            # print(graph[origin_num][destination_num].get(0))

            # Traffic avoidance, todo

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
