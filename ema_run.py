import route_model
import os

from ema_workbench import Model, RealParameter, ScalarOutcome
from ema_workbench import MultiprocessingEvaluator, ema_logging

from ema_workbench import save_results


"""
Main method to run the experiment of the fugitive route choice model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are saved into a file. 
"""
if __name__ == "__main__":

    route_model_instance = route_model.route_model()

    model = Model('routemodel', function=route_model_instance.run_model)

    # specify uncertainties
    model.uncertainties = [
        RealParameter("CA", 1, 2),
        RealParameter("OA", 1, 2),
        RealParameter("LP", 0.5, 1),
        RealParameter("RP", 0.5, 2),
        RealParameter("WW", 0.5, 2),
        RealParameter("HS", 0.5, 1),
        RealParameter("SR", 0.5, 1),
        RealParameter("TA", 1, 2),
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

    with MultiprocessingEvaluator(model, n_processes=os.cpu_count()) as evaluator:
        results = evaluator.perform_experiments(scenarios=64)

    save_results(results, 'results/first_run_allpoints_10scenarios.gz')
