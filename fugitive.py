import numpy as np
from pydsol.model.entities import Entity
import itertools


class Fugitive(Entity):

    id_iter_fug = itertools.count(1)

    def __init__(self, simulator, t, **kwargs):
        # self.speed = np.random.triangular(0, 30, 50)  # km/h to day
        self.speed = 500 #30 km/h is 500 m per minuut
        super().__init__(simulator, t, self.speed, **kwargs)

        self.name = f"{self.__class__.__name__} {str(next(self.id_iter_fug))}"
        self.route_planned = []

        self.output_route = {}




