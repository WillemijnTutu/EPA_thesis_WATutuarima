# Fugitive route-seeking model

The fugitive route-seeking model in this GitHub Repository is a python package which can be used to run a discrete event simulation model which simulates the fugitive route seeking behaviour to create a network of possible escape routes takes by a criminal after a criminal offence. This simulation model is part of the EPA Master thesis course of the Engineering and Policy Analysis MSc program at the Delft University of Technology.

## Installation

The model is based on two packages that combine discrete event modelling and network based models.

The first package that is required to run the model is the PyDSOL-model package (version 0.1) which can be installed using the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
pip install git+https://github.com/imvs95/pydsol-model.git
```
The second required package is the PyDSOL-core package which is required to be downloaded from the GitHub repository and added to the folder where the model is running. This package can be found [here](https://github.com/averbraeck/pydsol-core)

## To run the model

Launch the simulation model with visualization
```
    $ python run_simulation.py
```

## Files

Python files:
* [basic_logger.py](basic_logger.py): Python script to create a basic logger for the simulation model.

* [fugitive.py](fugitive.py): File that includes the Fugitive class to construct a fugitive entity

* [fugtive_model.py](fugitive_model.py): File that includes the main model class which is used to construct all the model components

* [road_components.py](road_components.py): File that includes all the classes of the components that the simulation model consists of.

* [run_simulation.py](run_simulation.py): File that creates the model, this is the file where the experimental setup can be specified.

Graph folder:
* [delft.graphml](delft.graphml): Graph representation of the Delft road network
* [delft_drive.graphml](delft_drive.graphml): Graph representation of the Delft road network that only includes roads utilized by cars
* [rdm.graphml](rdm.graphml): Graph representation of the Rotterdam road network
* [rotterdam_drive.graphml](rotterdam_drive.graphml): Graph representation of the Rotterdam road network where only car roads are included
* [rotterdam_drive_with_cameras.graphml](rotterdam_drive_with_cameras.graphml): Graph representation of the Rotterdam road network where only car roads are included and cameras are added based on node locations
* [rotterdam_drive_with_cameras_on_edges.graphml](rotterdam_drive_with_cameras_on_edges.graphml): Graph representation of the Rotterdam road network where only car roads are included and cameras are added based on edge locations

Data folder:
* [bridges](bridges): Folder with bridge data and queries from OSM
* [cameras](cameras): Folder with camera location data from Politie
* [roundabouts](roundabouts): Folder with roundabout data and queries from OSM
* [traffic](traffic): Folder with traffic related data
* [traffic_lights](traffic_lights): Folder with traffic lights data and queries from OSM

Notebooks folder:
* [create_graph_rotterdam.ipynb](create_graph_rotterdam.ipynb): Code to create the initial road graph of Rotterdam
* [get_random_points.ipynb](get_random_points.ipynb): Code to generate random points on the map
* [camera_data_merge.ipynb](camera_data_merge.ipynb): Code to merge graph data with camera data
* [traffic_points.ipynb](traffic_points.ipynb): Code to generate pairs of nodes to calculate traffic on
