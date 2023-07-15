import route_model_vis


if __name__ == "__main__":

    route_model_instance = route_model_vis.route_model()

    RP = [0.1, 0.3, 0.6, 0.8, 1.0]
    HS = [0.1, 0.3, 0.6, 0.8, 1.0]
    OA = [1, 2, 3, 4, 5]
    TA = [1, 2, 3, 4, 5]

    for RP_value in RP:
        route_model_instance.run_model(seed=1000, RP=RP_value)

    for HS_value in HS:
        route_model_instance.run_model(seed=1000, HS=HS_value)

    for OA_value in OA:
        route_model_instance.run_model(seed=1000, OA=OA_value)

    for TA_value in TA:
        route_model_instance.run_model(seed=1000, TA=TA_value)

