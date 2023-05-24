import route_model
from ema_workbench import Model, RealParameter, ScalarOutcome, ema_logging, perform_experiments
from ema_workbench.analysis import pairs_plotting
from ema_workbench import MultiprocessingEvaluator, ema_logging, perform_experiments

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from ema_workbench import save_results


"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":
    model = Model('routemodel', function=route_model.route_model)

    # specify uncertainties
    model.uncertainties = [
        RealParameter("CA", 0.7, 1),
        RealParameter("OA", 0.7, 1),
        RealParameter("LP", 0.7, 1),
        RealParameter("RP", 0.7, 1),
        RealParameter("WW", 0.7, 1),
        RealParameter("HS", 0.7, 1),
        RealParameter("SR", 0.7, 1),
        RealParameter("TA", 0.7, 1),
    ]

    # specify outcomes
    model.outcomes = [
        ScalarOutcome("degree_centrality_mean_mean"),
        ScalarOutcome("degree_centrality_mean_var"),
        ScalarOutcome("degree_centrality_var_mean"),
        ScalarOutcome("degree_centrality_var_var"),
        ScalarOutcome("betweenness_centrality_mean_mean"),
        ScalarOutcome("betweenness_centrality_mean_var"),
        ScalarOutcome("betweenness_centrality_var_mean"),
        ScalarOutcome("betweenness_centrality_var_var")
    ]

    ema_logging.log_to_stderr(ema_logging.INFO)

    with MultiprocessingEvaluator(model, n_processes=7) as evaluator:
        results = evaluator.perform_experiments(scenarios=10)


    fig, axes = pairs_plotting.pairs_scatter(results[0], results[1], legend=False)
    fig.set_size_inches(8, 8)
    plt.show()

    save_results(results, '1000 scenarios 5 policies.tar.gz')

