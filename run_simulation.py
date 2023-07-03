import route_model_vis

from ema_workbench import Model, RealParameter, ScalarOutcome, BooleanParameter, Samplers
from ema_workbench import MultiprocessingEvaluator, ema_logging

from ema_workbench import save_results


import osmnx as ox
import numpy as np

"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":

    route_model_instance = route_model_vis.route_model()

    # print(route_model_instance.run_model(seed=1000))
    #
    # b = np.load('OA1LP1RP1OW1HS1TA1.npy', allow_pickle=True)
    # print(b)

    value_OA = [1, 5]
    value_HS = [0.1, 1]
    values_LP = [0.1, 1]
    values_OW = [1, 5]
    values_RP = [0.1, 1]
    values_TA = [1, 5]

    for OA in value_OA:
        for HS in value_HS:
            for LP in values_LP:
                for OW in values_OW:
                    for RP in values_RP:
                        for TA in values_TA:
                            print(route_model_instance.run_model(seed=1000, OA=OA, HS=HS, LP=LP, OW=OW, RP=RP, TA=TA))

    exit(0)

    source = 670854737
    sink = [44254038, 44341323, 670854737, 44448306, 3161262011, 44232104, 44176183, 44532514, 1680069937, 44613980]



    default_graph_file_path = "graph/graph_base_case.graphml"
    graph_OW_False = ox.load_graphml(default_graph_file_path)

    node_colors = []
    node_size = []
    edge_colors = []
    edge_size = []
    for index in graph_OW_False.nodes():
        if index in sink and index != source:
            node_colors.append('tab:blue')
            node_size.append(30)
        elif index == source:
            node_colors.append('red')
            node_size.append(30)
        # elif index in route_1:
        #     node_size.append(1)
        #     node_colors.append('black')
        # elif index in route_2:
        #     node_size.append(1)
        #     node_colors.append('orange')
        # elif index in route_3:
        #     node_size.append(1)
        #     node_colors.append('yellow')
        else:
            node_colors.append("lightgray")
            node_size.append(0)

    # for (u, v) in graph_OW_False.edges():
    #     if (u, v) in edges_1:
    #         edge_colors.append('black')
    #         edge_size.append(2)
    #     elif (v, u) in edges_1:
    #         edge_colors.append('black')
    #         edge_size.append(2)
    #     elif (u, v) in edges_2:
    #         edge_colors.append('orange')
    #         edge_size.append(2)
    #     elif (v, u) in edges_2:
    #         edge_colors.append('orange')
    #         edge_size.append(2)
    #     elif (u, v) in edges_3:
    #         edge_colors.append('yellow')
    #         edge_size.append(2)
    #     elif (v, u) in edges_3:
    #         edge_colors.append('yellow')
    #         edge_size.append(2)
    #     else:
    #         edge_colors.append('lightgray')
    #         edge_size.append(0.5)

    file_path = "test.png"


    ox.plot.plot_graph(
        graph_OW_False,
        bgcolor="white", node_color=node_colors, node_size=node_size,
        show=False, save=True, filepath=file_path
    )
    #
    # ox.plot.plot_graph(
    #     graph_OW_False,
    #     bgcolor="white", node_color=node_colors, node_size=node_size, edge_linewidth=edge_size,
    #     edge_color=edge_colors,
    #     show=False, save=True, filepath=file_path
    # )
