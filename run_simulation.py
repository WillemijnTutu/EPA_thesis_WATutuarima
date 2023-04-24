import fugitive_model

from pydsol.core.simulator import DEVSSimulatorFloat
from pydsol.core.experiment import SingleReplication

import logging
from pydsol.model.basic_logger import get_module_logger

logger = get_module_logger(__name__, level=logging.DEBUG)

"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":
    simulator = DEVSSimulatorFloat("sim")

    filepath = "graph/delft_drive.graphml"
    model = fugitive_model.FugitiveModel(simulator, filepath)
    replication = SingleReplication("rep1", 0.0, 0.0, 15)
    simulator.initialize(model, replication)
    simulator.start()

    model.get_output_statistic()
