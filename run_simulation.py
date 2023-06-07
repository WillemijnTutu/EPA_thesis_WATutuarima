import route_model
import time
import os

from ema_workbench import Model, RealParameter, ScalarOutcome
from ema_workbench import MultiprocessingEvaluator, ema_logging

from ema_workbench import save_results

"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":
    print(os.cpu_count())

    # model = route_model.route_model()
    #
    # print(model.run_model())

