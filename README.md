# Fugitive route-seeking model

The fugitive route-seeking model in this GitHub Repository is a python package which can be used to run a model which simulates the fugitive route seeking behaviour to create a network of possible escape routes takes by a criminal after a criminal offence. This simulation model is part of the EPA Master thesis course of the Engineering and Policy Analysis MSc program at the Delft University of Technology.

## To run the model

Launch the simulation model with visualization
```
    $ python run_simulation.py
```

## Files

### Python files:
* [ema_run.py](ema_run.py): Python script to run the model using a configuration of the EMA workbench package.
* [model_visualisaion.py](model_visualisaion.py): Python script to run the visualisation tool of the model.
* [route_model.py](route_model.py): File that includes the main functionality of the route choice model.
* [run_simulation.py](run_simulation.py): Python script to initiate and run a single instance of the route choice model.


### Notebooks folder:
* [create_graph_rotterdam.ipynb](create_graph_rotterdam.ipynb): Code to create the initial road graph of Rotterdam
* [get_random_points.ipynb](get_random_points.ipynb): Code to generate random points on the map
* [data_integration.ipynb](data_integration.ipynb): Code to merge all data files with the graph

### Graph folder:

This folder includes all the graph files that were created during the development of the final graph used in the simulation. These graphs have been created using the code found in [Notebooks](Notebooks). The graph used in simulation can be found [here](rotterdam_drive_bbox_cameras_traffic_lights_bridges_roundabouts_tunnels.graphml).

### Data folder:
* [bridges](bridges): Folder with bridge data and queries from OSM
* [cameras](cameras): Folder with camera location data from Politie
* [roundabouts](roundabouts): Folder with roundabout data and queries from OSM
* [traffic](traffic): Folder with traffic related data
* [traffic_lights](traffic_lights): Folder with traffic lights data and queries from OSM
* [tunnels](tunnels): Folder with traffic lights data and queries from OSM
