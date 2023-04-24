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
