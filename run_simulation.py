import run_model

"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":

    runner = run_model.RunModel()
    runner.run_replication("rational_length")


