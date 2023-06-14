import route_model_vis
import math

"""
Main method to run the experiment of the fugitive model

Here the experimental setup is inserted into the model and the number of replications is determined
After the model is run, the output statistics are displayed. 
"""
if __name__ == "__main__":

    model = route_model_vis.route_model_vis()

    seed = 2222

    # seed = 3333

    print(model.run_model(seed=seed, rational=False, one_way_possible=True))
    #
    # print(model.run_model(seed=seed, TA1=2))
    # print(model.run_model(seed=seed, TA1=3))
    # print(model.run_model(seed=seed, TA1=4))
    # print(model.run_model(seed=seed, TA1=5))



#     TA1 waarde 1-4 geven nog andere resultaten hoger niet
#     TA2 zelfde
#     TA3

#      CA waarde 50 geeft verschil daarboven niet 70 -> 75
#       Ca waardes [1, 500]

#       OA waardes [1, 500]
    # geprobeerd 5, 50,500,5000, geen verschil tussen 500 en 5000, geen verschil > 300

#   LP waardes [0.2, 1]





