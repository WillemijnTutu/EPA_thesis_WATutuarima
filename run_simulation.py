import route_model
import time

from ema_workbench import Model, RealParameter, ScalarOutcome, ema_logging, perform_experiments
from ema_workbench.analysis import pairs_plotting
from ema_workbench import MultiprocessingEvaluator, ema_logging, perform_experiments

import matplotlib.pyplot as plt

from ema_workbench import save_results



"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":

    start_time = time.time()

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
        ScalarOutcome("num_of_nodes"),
        ScalarOutcome("num_of_edges"),
        ScalarOutcome("continuity_mean"),
        ScalarOutcome("continuity_vars"),
        ScalarOutcome("connectivity_mean"),
        ScalarOutcome("connectivity_vars"),
        ScalarOutcome('degree_centrality_mean'),
        ScalarOutcome('degree_centrality_var'),
        ScalarOutcome('betweenness_centrality_mean'),
        ScalarOutcome('betweenness_centrality_var')
    ]

    ema_logging.log_to_stderr(ema_logging.INFO)

    with MultiprocessingEvaluator(model, n_processes=7) as evaluator:
        results = evaluator.perform_experiments(scenarios=1)

    save_results(results, 'results.gz')
    print("--- %s seconds ---" % (time.time() - start_time))

