import osmnx as ox
import networkx as nx

default_start_points = [44430463]
default_destination_points = [44465861]
default_graph_file_path = "graph/rotterdam_drive_with_cameras_on_edges.graphml"
default_num_of_paths = 5

strategies = {
    1: [1, 1, 1, 1, 1, 1, 1, 1, True],
    2: [1, 1, 1, 1, 1, 1, 1, 1, True],
    3: [1, 1, 1, 1, 1, 1, 1, 1, False],
    4: [1, 1, 1, 1, 1, 1, 1, 1, False]
}


class route_model():

    def __init__(self, start_points=default_start_points, destination_points=default_destination_points,
                 graph_file_path=default_graph_file_path, num_of_paths=default_num_of_paths, graph=None
                 ):
        self.start_points = start_points
        self.destination_points = destination_points
        self.graph_file_path = graph_file_path
        self.num_of_paths = num_of_paths
        # load graph

        self.graph = graph
        if graph is None:
            self.graph = self.load_graph()

        self.original_graph = self.graph.copy()
        self.undirected_graph = self.graph.copy().to_undirected()

        # simulator = None
        # model = None

    def load_graph(self):
        return ox.load_graphml(self.graph_file_path)

    def run_model(self, rational=True, CA=1, OA=1, LP=1, RP=1, WW=1, HS=1, SR=1, TA=1,
                  num_of_paths=default_num_of_paths,
                  one_way_possible=False, start_strategy=1, end_strategy=1, strategy_change_percentage=1):

        if rational:
            if one_way_possible:
                self.graph = self.undirected_graph.copy()
            else:
                self.graph = self.original_graph.copy()

            self.calculate_weights(CA, OA, LP, RP, WW, HS, SR, TA)
            self.num_of_paths = num_of_paths
            return self.run_rational_model()

        else:
            if strategies[start_strategy][-1]:
                self.graph = self.undirected_graph.copy()
            else:
                self.graph = self.original_graph.copy()

            self.calculate_weights(*strategies[start_strategy][: -1])
            self.num_of_paths = num_of_paths

            return self.run_irrational_model(end_strategy, strategy_change_percentage)

    def run_rational_model(self):
        # calculate weights

        degree_centrality_means = []
        degree_centrality_vars = []
        betweenness_centrality_means = []
        betweenness_centrality_vars = []

        for source in self.start_points:
            # create empty graph
            route_graph = nx.Graph()
            for sink in self.destination_points:
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                      weight="used_weight")  # cpus=1??

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

            # file_path = "results/rational_" + mode + ".graphml"
            # nx.write_graphml_lxml(route_graph, file_path)

            stats = self.calculate_statistics(route_graph)
            degree_centrality_means.append(stats[0])
            degree_centrality_vars.append(stats[1])
            betweenness_centrality_means.append(stats[2])
            betweenness_centrality_vars.append(stats[3])

        degree_centrality_mean_mean = sum(degree_centrality_means) / len(degree_centrality_means)
        degree_centrality_mean_var = sum((i - degree_centrality_mean_mean) ** 2 for i in degree_centrality_means) / len(
            degree_centrality_means)

        degree_centrality_var_mean = sum(degree_centrality_vars) / len(degree_centrality_vars)
        degree_centrality_var_var = sum((i - degree_centrality_var_mean) ** 2 for i in degree_centrality_vars) / len(
            degree_centrality_vars)

        betweenness_centrality_mean_mean = sum(betweenness_centrality_means) / len(betweenness_centrality_means)
        betweenness_centrality_mean_var = sum(
            (i - betweenness_centrality_mean_mean) ** 2 for i in betweenness_centrality_means) / len(
            betweenness_centrality_means)

        betweenness_centrality_var_mean = sum(betweenness_centrality_vars) / len(betweenness_centrality_vars)
        betweenness_centrality_var_var = sum(
            (i - betweenness_centrality_var_mean) ** 2 for i in betweenness_centrality_vars) / len(
            betweenness_centrality_vars)

        return {
            'degree_centrality_mean_mean': degree_centrality_mean_mean,
            'degree_centrality_mean_var': degree_centrality_mean_var,
            'degree_centrality_var_mean': degree_centrality_var_mean,
            'degree_centrality_var_var': degree_centrality_var_var,
            'betweenness_centrality_mean_mean': betweenness_centrality_mean_mean,
            'betweenness_centrality_mean_var': betweenness_centrality_mean_var,
            'betweenness_centrality_var_mean': betweenness_centrality_var_mean,
            'betweenness_centrality_var_var': betweenness_centrality_var_var,
        }

    def run_irrational_model(self, end_strategy, strategy_change_percentage):
        degree_centrality_means = []
        degree_centrality_vars = []
        betweenness_centrality_means = []
        betweenness_centrality_vars = []

        for source in self.start_points:
            # create empty graph
            route_graph = nx.Graph()
            for sink in self.destination_points:
                routes = ox.distance.k_shortest_paths(self.graph, source, sink, self.num_of_paths,
                                                      weight="used_weight")  # cpus=1??

                for route in routes:
                    adjusted_routes = []

                    index_to_change = int(len(route) * strategy_change_percentage)
                    routes_to_adjust = ox.distance.k_shortest_paths(self.graph, route[index_to_change], sink,
                                                                    self.num_of_paths,
                                                                    weight="used_weight")  # cpus=1??

                    for route_to_adjust in routes_to_adjust:
                        adjusted_routes.append(route[0:index_to_change - 1] + route_to_adjust) #is indexing correct??

                    for adjusted_route in adjusted_routes:
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


            stats = self.calculate_statistics(route_graph)
            degree_centrality_means.append(stats[0])
            degree_centrality_vars.append(stats[1])
            betweenness_centrality_means.append(stats[2])
            betweenness_centrality_vars.append(stats[3])

        degree_centrality_mean_mean = sum(degree_centrality_means) / len(degree_centrality_means)
        degree_centrality_mean_var = sum((i - degree_centrality_mean_mean) ** 2 for i in degree_centrality_means) / len(
            degree_centrality_means)

        degree_centrality_var_mean = sum(degree_centrality_vars) / len(degree_centrality_vars)
        degree_centrality_var_var = sum((i - degree_centrality_var_mean) ** 2 for i in degree_centrality_vars) / len(
            degree_centrality_vars)

        betweenness_centrality_mean_mean = sum(betweenness_centrality_means) / len(betweenness_centrality_means)
        betweenness_centrality_mean_var = sum(
            (i - betweenness_centrality_mean_mean) ** 2 for i in betweenness_centrality_means) / len(
            betweenness_centrality_means)

        betweenness_centrality_var_mean = sum(betweenness_centrality_vars) / len(betweenness_centrality_vars)
        betweenness_centrality_var_var = sum(
            (i - betweenness_centrality_var_mean) ** 2 for i in betweenness_centrality_vars) / len(
            betweenness_centrality_vars)

        return {
            'degree_centrality_mean_mean': degree_centrality_mean_mean,
            'degree_centrality_mean_var': degree_centrality_mean_var,
            'degree_centrality_var_mean': degree_centrality_var_mean,
            'degree_centrality_var_var': degree_centrality_var_var,
            'betweenness_centrality_mean_mean': betweenness_centrality_mean_mean,
            'betweenness_centrality_mean_var': betweenness_centrality_mean_var,
            'betweenness_centrality_var_mean': betweenness_centrality_var_mean,
            'betweenness_centrality_var_var': betweenness_centrality_var_var,
        }

    def calculate_weights(self, CA, OA, LP, RP, WW, HS, SR, TA):
        for road_id, (origin_num, destination_num, data) in enumerate(self.graph.edges(data=True)):
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

    def calculate_statistics(self, route_graph):
        degree_centrality = list(nx.degree_centrality(route_graph).values())
        degree_centrality_mean = sum(degree_centrality) / len(degree_centrality)
        degree_centrality_var = sum((i - degree_centrality_mean) ** 2 for i in degree_centrality) / len(
            degree_centrality)

        betweenness_centrality = list(nx.betweenness_centrality(route_graph).values())
        betweenness_centrality_mean = sum(betweenness_centrality) / len(betweenness_centrality)
        betweenness_centrality_var = sum((i - betweenness_centrality_mean) ** 2 for i in betweenness_centrality) / len(
            betweenness_centrality)

        return [degree_centrality_mean, degree_centrality_var, betweenness_centrality_mean, betweenness_centrality_var]

        # add statistics in excel

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

    def run_bounded_rational_model(self, mode):
        return
