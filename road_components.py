from pydsol.model.node import Node
from pydsol.model.link import Link
from pydsol.model.source import Source
from fugitive import Fugitive
import math
import osmnx as ox

import logging
from basic_logger import get_module_logger
logger = get_module_logger(__name__, level=logging.INFO)


class Intersection(Node):
    def __init__(self, simulator, capacity=math.inf, **kwargs):
        super().__init__(simulator, **kwargs)

        self.id = kwargs["id"]
        self.next = []

    def enter_input_node(self, entity, **kwargs):
        super().enter_input_node(entity, **kwargs)
        logger.debug(f"Time {self.simulator.simulator_time:.2f}: Entity: {entity.name} entered node{self.name}")

        #save route
        entity.output_route[self.simulator.simulator_time] = self.id

    def exit_output_node(self, entity, **kwargs):

        assert self.id == entity.route_planned[0]

        if len(entity.route_planned) <= 1:  # reached destination node
            logger.debug(f"Time {self.simulator.simulator_time:.2f}: {entity.name} has reached destination node {self.id}")

        elif self.id == entity.route_planned[1]:  # next node is the current node; i.e., posting
            entity.route_planned.pop(0)
            self.simulator.schedule_event_rel(1, self, "enter_input_node", entity=entity)

        else:
            try:
                entity.route_planned.pop(0)  # remove current node from planned route
                next_node = entity.route_planned[0]

                for link in self.next:
                    if link.destination_name == next_node:
                        destination_link = link
                        destination_link.enter_link(entity)  # stel er zijn twee links naar de next_node gaat het hier mis -> break na deze if

                        logger.debug("Time {0:.2f}: Entity: {1} exited node{2}".format(self.simulator.simulator_time,
                                                                                      entity.name, self.id))
                        break

                if 'destination_link' not in locals():
                    raise Exception(f'The destination node {next_node} of {entity.name} is not an output link of the current node {self.name}')

            except AttributeError:
                raise AttributeError(f"{self.name} has no output link")


class Road(Link):
    def __init__(self, simulator, origin, destination, length, selection_weight=1, **kwargs):
        super().__init__(simulator, origin, destination, length, selection_weight, **kwargs)
        self.next = destination
        self.road_id = kwargs["road_id"]

        self.destination_name = kwargs["destination_name"]

    def enter_link(self, entity, **kwargs):
        super().enter_link(entity)

class SourceFugitive(Source):
    def __init__(self, graph, simulator, interarrival_time="default", num_entities=1, **kwargs):
        super().__init__(simulator, interarrival_time, num_entities, **kwargs)

        self.id = kwargs['id']

        self.entity_type = Fugitive
        self.entities_created = None
        self.fugitive_sink = kwargs["fugitive_sink"]
        self.graph = graph

    def exit_source(self, entity, **kwargs):
        super().exit_source(entity, **kwargs)

        entity.route_planned = ox.distance.shortest_path(self.graph, self.id, self.fugitive_sink, weight='length', cpus=1)
        print(entity.route_planned)

        self.entities_created = entity
