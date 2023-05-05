import numpy as np
import math
import logging

from pydsol.model.node import Node
from pydsol.model.link import Link
from pydsol.model.source import Source
from pydsol.model.sink import Sink
from fugitive import Fugitive
from basic_logger import get_module_logger

logger = get_module_logger(__name__, level=logging.INFO)

"""
    This file includes all the classes that are used to build a network in the fugitive route seeking model
    
    Classes
    -------
    Intersection:Node
        Class that creates an intersection to connect one or more road components. The functionality of an intersection
        includes the decision making of the fugitive entity per node. 
    Road:Link
        Class that creates an road component that connects two intersection components.
    SourceFugitive:Source
        Class that creates a source component which creates the fugitive entities
    SinkFugitive:Sink
        This class creates a fugitive sink component 
"""


class Intersection(Node):
    """
    Class that creates an intersection to connect one or more road components. The functionality of an intersection
    includes the decision-making of the fugitive entity per node.

    Attributes
    ----------
    simulator:
        PyDSOL core simulator
    capacity: int
    kwargs:
        the keyword arguments that are used to expand the Node class
        id: int
            Personal id number of the intersection component
    next:Array
        List of edges that are connected to the node

    Methods
    ------
    __init__
        Method to initialise the intersection component
    enter_input_node
        Method to enter the intersection
    exit_output_node
        Method to exit the link by selecting a link on which the entity should travel to the next destination

    """

    def __init__(self, simulator, capacity=math.inf, **kwargs):
        """
        Method to initialise the intersection component

        Parameters
        ----------
        simulator:
            PyDSOL core simulator
        capacity: int
            Maximum number of entities that can be present at an intersection
        kwargs:
            the keyword arguments that are used to expand the Node class
            id: int
                Personal id number of the intersection component
        """
        super().__init__(simulator, **kwargs)

        self.id = kwargs["id"]
        self.next = []

    def enter_input_node(self, entity, **kwargs):
        """
        Method to enter the intersection

        Parameters
        ----------
        entity: Entity
        kwargs:
            the keyword arguments that are used to expand the enter_input_node method
        """

        super().enter_input_node(entity, **kwargs)
        logger.debug(f"Time {self.simulator.simulator_time:.2f}: Entity: {entity.name} entered node{self.name}")

        # save route
        entity.output_route[self.simulator.simulator_time] = self.id

    def exit_output_node(self, entity, **kwargs):
        """
        Method to exit the link by selecting a link on which the entity should travel to the next destination

        Parameters
        ----------
        entity: Entity
        kwargs:
            the keyword arguments that are used to expand the exit_output_node method

        Raises
        ------
        AssertionError
            If the intersection is not found on the route of the entity
        """

        assert self.id == entity.route_planned[0]

        if len(entity.route_planned) <= 1:  # reached destination node
            logger.debug(f"Time {self.simulator.simulator_time:.2f}: {entity.name} has reached "
                         f"destination node {self.id}")

            self.next.enter_link(entity)

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
                        destination_link.enter_link(entity)
                        # stel er zijn twee links naar de next_node gaat het hier mis -> break na deze if

                        logger.debug("Time {0:.2f}: Entity: {1} exited node{2}".format(self.simulator.simulator_time,
                                                                                      entity.name, self.id))
                        break

                if 'destination_link' not in locals():
                    raise Exception(f'The destination node {next_node} of {entity.name} '
                                    f'is not an output link of the current node {self.name}')

            except AttributeError:
                raise AttributeError(f"{self.name} has no output link")


class Road(Link):
    """
    Class that creates an road component that connects two intersection components.

    Attributes
    ----------
    simulator:
        PyDSOL core simulator
    origin: Intersection
        Starting point of the road component
    destination: Intersection
        End point of the road component
    length: int
        Length in KM
    selection_weight: int
        Weight used to calculate preference for route choices

    Methods
    -------
    __init__
        Method to initialise a road component
    """

    def __init__(self, simulator, origin, destination, length, selection_weight=1, **kwargs):
        """
        Method to initialise a road component

        Parameters
        ----------
        simulator:
            PyDSOL core simulator
        origin: Intersection
            Starting point of the road component
        destination: Intersection
            End point of the road component
        length: int
            Length in KM
        selection_weight: int
             Weight used to calculate preference for route choices
        kwargs:
            the keyword arguments that are used to expand the Link class
        """

        super().__init__(simulator, origin, destination, length, selection_weight, **kwargs)
        self.next = destination
        self.road_id = kwargs["road_id"]

        self.destination_name = kwargs["destination_name"]


class SourceFugitive(Source):
    """
    Class that construct a source that creates a fugitive entity

    Attributes
    ----------
    graph:osmnx.graph
        graph that represents the network
    simulator:
        PyDSOL core simulator
    interarrival_time:str
        time between the creation of entities. Default is np.random.exponential(0.25).
    num_entities:int
        number of entities that the source creates
    id:int
        Identification number of source
    fugitive_sink:Node
        Node that is the final destination of the fugitive entity
    entity_type:Class
        The entity type that the source creates, in this case the type is Fugitive
    entity_mode:Array
        An array representing the mental mode of the fugitive

    Methods
    -------
    __init__
        Method to initialise the fugitive source component
    create_entities
        Create fugitives via SimEvent, given the interarrival time and the number of entities.
    exit_source
        Method for an entity to exit the source component
    """

    def __init__(self, graph, simulator, num_entities=1, **kwargs):
        """
        Method to initialise the fugitive source component

        Parameters
        ----------
        graph: osmnx.graph
            graph that represents the network
        simulator:
            PyDSOL core simulator
        interarrival_time:str
            time between the creation of entities. Default is np.random.exponential(0.25).
        num_entities: int
            number of entities that the source creates
        kwargs:
            the keyword arguments that are used to expand the Source class
            id: int
                Identification number of source
            fugitive_sink: Node
                Node that is the final destination of the fugitive entity
        """
        self.id = kwargs['id']

        self.entity_type = Fugitive
        self.entities_created = None
        self.fugitive_sink = kwargs["fugitive_sink"]
        self.fugitive_source = kwargs["fugitive_source"]
        self.graph = graph

        self.simulator = simulator
        self.num_entities = num_entities

        self.next = None  # this should be the next process
        self.interarrival_time = np.random.exponential(0.25)

        self.entity_mode = kwargs['mental_mode']

        self.kwargs = kwargs

        self.name = "{0} {1}".format(self.__class__.__name__, str(self.id))
        if "name" in kwargs:
            self.name = kwargs["name"]

        if "distribution" in kwargs:
            self.distribution = kwargs["distribution"]

        self.simulator.schedule_event_now(self, "create_entities")

    def create_entities(self, **kwargs):
        """
        Create fugitives via SimEvent, given the interarrival time and the number of entities.

        Parameters
        ----------
        kwargs:
            kwargs are the keyword arguments that are used to invoke the method or expand the function.

        """

        # Create new entity
        for _ in range(self.num_entities):
            entity = Fugitive(self.simulator, self.simulator.simulator_time, self.entity_mode, self.graph,
                              self.fugitive_sink, self.fugitive_source, **kwargs)
            # logger.info("Time {0:.2f}: {1} is created at {2}".format(self.simulator.simulator_time, entity.name))
            self.exit_source(entity)

    def exit_source(self, entity, **kwargs):
        """
        Method to exit the source component

        Parameters
        ----------
        entity: Entity
        kwargs:
            the keyword arguments that are used to expand the exit_source method
        """
        super().exit_source(entity, **kwargs)

        self.entities_created = entity


class SinkFugitive(Sink):
    """
    This class creates a fugitive sink component

    Attributes
    ----------
    simulator:
        PyDSOL core simulator
    transfer_in_time: [float, int]
        time it takes to transfer an object into the sink. Default is 0.
    model:FugitiveModel
            The model that uses the road_component
    entities_of_system=Array
        Array of all the entities in the system created by the component

    Methods
    -------
    __init__
        Method to initialise class
    enter_input_node
        Method to call when entity enters a sink (output statistics)
    """

    def __init__(self, simulator, model, transfer_in_time: [float, int], **kwargs):
        """
        Method to initialise a fugitive sink component

        Parameters
        ----------
        simulator
            PyDSOL core simulator
        model:FugitiveModel
            The model that uses the road_component
        transfer_in_time: [float, int]
            time it takes to transfer an object into the sink. Default is 0.
        kwargs:
            kwargs are the keyword arguments that are used to expand the sink class.
            *name: str
                user-specified name for the sink.
        """

        super().__init__(simulator, transfer_in_time=transfer_in_time, **kwargs)

        self.model=model
        self.entities_of_system = []

    def enter_input_node(self, entity):
        """
        Method to call when entity enters a sink (output statistics)

        Parameters
        ----------
        entity:fugitive
            Fugitive entity on which to calculate the output statistics
        """

        self.model.get_output_statistic(entity)
        super().enter_input_node(entity)
