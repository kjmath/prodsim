"""Collection of classes for prod-sim"""
import numpy as np

class Process:

    def __init__(self, name, prob_dist, params, buffer_cap):
        '''Create a production process object.

        Arguments:
            name (string): Unique name of the process.
            prob_dist (string): probability distrubtion characterizing the process 
                time, choose from a numpy.random distribution 
                (see numpy.random documentation at SciPy.org).
            params (dict): dictionary of parameters for selected process time
                distribution, in simulator time units; use parameter names given 
                for numpy.random distributions as keys for dictionary.
            buffer_cap(scalar or None): maximum buffer capacity BEFORE the process station, 
                use None for infinite buffer.

        '''
        self.name = name
        self.prob_dist = prob_dist 
        self.params = params 
        self.buffer_cap = buffer_cap 
        self.part_in_process = None # instance of PartType in process, or None
        self.parts_in_buffer = [] # list of PartType instances in buffer, index 0 is first in line
        self.process_completion_time = 0 # initialize time of next completed process

    def start_process(self, prod_time):
        '''start the process: update completion time, move first part in buffer
            to in process.'''

        if self.part_in_process is None:
            if self.parts_in_buffer:
                self.update_completion_time(prod_time)
                self.part_in_process = self.parts_in_buffer[0]
                self.remove_first_in_buffer()


    def get_process_time(self):
        '''Get process time for next process from probability distribution.

        Returns:
            scalar: process time [units: simulator time units].
        '''

        prob_dist_func = getattr(np.random, self.prob_dist)
        process_time = prob_dist_func(**self.params)
        return process_time

    def update_completion_time(self, prod_time):
        ''' Update the process_completion_time attribute.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        self.process_completion_time = self.get_process_time() + prod_time

    def is_buffer_full(self):
        '''Check if buffer BEFORE process is full.

        Returns:
            boolean: True if buffer is full, False otherwise.
        '''

        if self.buffer_cap is None:
            return False
        elif len(self.parts_in_buffer) < self.buffer_cap:
            return False
        else:
            return True

    def add_to_buffer(self, part):
        '''Add part to end of buffer.'''

        self.parts_in_buffer.append(part)

    def remove_first_in_buffer(self):
        '''Remove part from first position in buffer.'''

        self.parts_in_buffer = self.parts_in_buffer[1:]


class PartType:

    def __init__(self, name, arrival_prob_dist, arrival_params):
        '''Create a part type object.

        Arguments:
            name (string): unique string name for part type.
            arrival_prob_dist (string): probability distrubtion characterizing the 
                interarrival time, choose from a numpy.random distribution 
                (see numpy.random documentation at SciPy.org).
            arrival_params (dict): dictionary of parameters for selected interarrival 
                time distribution, in simulator time units; use parameter names given 
                for numpy.random distributions as keys for dictionary.
        '''
        self.name = name
        self.arrival_prob_dist = arrival_prob_dist
        self.arrival_params = arrival_params


class ProductionLine:

    def __init__(self, part_type_name, process_stations):
        '''Create a production line object.

        Arguments:
            part_type_name (string): same string name of corresponding PartType object.
            process_stations (list): ordered list of Process objects representing the
                production line for the designated part type. 
        '''

        self.part_type_name = part_type_name
        self.process_stations = process_stations

    def end_process(process):
        pass


class Factory:

    def __init__(self, prod_lines):
        '''Create a factory object.

        Arguments:
            prod_lines (string): same string name of corresponding PartType object.
            process_stations (list): ordered list of Process objects representing the
                production line for the designated part type. 
        '''

        self.prod_lines = prod_lines

        all_processes = []
        crit_time_dict = {}
        buffer_full_dict = {}
        for line in prod_lines:
            for process in line.process_stations:
                if process.name not in crit_time_dict:
                    all_processes.append(process)
                    crit_time_dict[process.name] = 0
                    buffer_full_dict[process.name] = False
        self.all_processes = all_processes
        self.crit_time_dict = crit_time_dict
        self.buffer_full_dict = buffer_full_dict

    def update_production(self):

        pass

    def update_crit_times(self):

        pass

    def update_buffer_full_dict(self):

        pass
