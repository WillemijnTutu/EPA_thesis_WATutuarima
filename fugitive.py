from pydsol.model.entities import Entity
import itertools


class Fugitive(Entity):
    """
    Class used to simulate a fugitive entity

    Parameters
    ----------
    simulator:
        PyDSOL core simulator
    t:int
        time_creations
    kwargs:
        the keyword arguments that are used to expand the entity class
    """

    id_iter_fug = itertools.count(1)

    def __init__(self, simulator, t, **kwargs):
        """
        Method to initialise fugitive entity
        """

        self.speed = 500
        # 30 km/h is 500 m per minuut
        super().__init__(simulator, t, self.speed, **kwargs)

        self.name = f"{self.__class__.__name__} {str(next(self.id_iter_fug))}"
        self.route_planned = []

        self.output_route = {}




