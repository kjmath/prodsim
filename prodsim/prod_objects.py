"""Collection of classes for prod-sim"""
import numpy as np
from prodsim.helpers import weibull

class Process:

    def __init__(self, name, prob_dist, params, buffer_cap):
        '''Create a production process object. Assumes no more than one part can be 
            currently in the process.

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
        self.next_crit_time = 0 # initialize time of next completed process

    def start_process(self, prod_time):
        '''Start the process: update completion time, move first part in buffer
            to in process.'''
        if self.part_in_process is None:
            
            if self.parts_in_buffer:
                self.update_next_crit_time(prod_time)
                self.part_in_process = self.parts_in_buffer[0]
                self.remove_first_in_buffer()
                return True
            else:
                # set to 0 so simulator can move forward and try again on next iteration
                self.next_crit_time = 0 

        return False


    def get_next_crit_time(self):
        '''Get process time for next process from probability distribution.

        Returns:
            scalar: process time [units: simulator time units].
        '''

        if self.prob_dist == 'weibull': 
            prob_dist_func = weibull
        else:
            prob_dist_func = getattr(np.random, self.prob_dist)

        process_time = prob_dist_func(**self.params)
        return process_time

    def update_next_crit_time(self, prod_time):
        ''' Update the next_crit_time attribute.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        self.next_crit_time = self.get_next_crit_time() + prod_time

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

    def __init__(self, name, arrival_prob_dist, arrival_params, process_stations):
        '''Create a part type object.

        Arguments:
            name (string): unique string name for part type.
            arrival_prob_dist (string): probability distrubtion characterizing the 
                interarrival time, choose from a numpy.random distribution 
                (see numpy.random documentation at SciPy.org).
            arrival_params (dict): dictionary of parameters for selected interarrival 
                time distribution, in simulator time units; use parameter names given 
                for numpy.random distributions as keys for dictionary.
            process_stations (list of Process objects): ordered list of Process objects representing the
                production line for the part. 
        '''
        self.name = name
        self.arrival_prob_dist = arrival_prob_dist
        self.arrival_params = arrival_params
        self.process_stations = process_stations
        self.next_crit_time = 0
        self.num_arrivals = 0
        self.throughput = 0

    def get_next_crit_time(self):
        '''Get arrival time for next part from probability distribution.

        Returns:
            scalar: part arrival time [units: simulator time units].
        '''

        prob_dist_func = getattr(np.random, self.arrival_prob_dist)
        arrival_time = prob_dist_func(**self.arrival_params)
        return arrival_time

    def update_next_crit_time(self, prod_time):
        ''' Update the next_crit_time attribute.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        self.next_crit_time = self.get_next_crit_time() + prod_time

    def end_process(self, process):
        '''End a process and updates next process buffer, assuming process currently has 
            an in-process part moving in the current production line.

        Arguments:
            process (Process class object): process to be ended. 

        Returns:
            boolean: True if process ended, False if not
        '''
        
        if process in self.process_stations and process.part_in_process == self:
            proc_index = self.process_stations.index(process)

            # process is last process
            if proc_index == len(self.process_stations) - 1:
                process.part_in_process = None
                self.throughput += 1
                return True
            # process is not last process and next process has room in buffer
            elif not self.process_stations[proc_index + 1].is_buffer_full():
                process.part_in_process = None
                self.process_stations[proc_index + 1].add_to_buffer(self)
                return True

        process.next_crit_time = 0 # set to 0 so simulator can try ending on next critical time
        return False

    def add_arriving_part(self, prod_time):
        '''Add an arriving part to the buffer of the first process for the part, 
            assuming the buffer is not full. Update next critical time.
        
        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        first_process = self.process_stations[0]

        if not first_process.is_buffer_full():
            first_process.add_to_buffer(self)
            self.num_arrivals += 1

        self.update_next_crit_time(prod_time)


class Factory:

    def __init__(self, part_types):
        '''Create a factory object.

        Arguments:
            part_types (list of ProductionLine objects): list of production 
                lines in factory.
        '''

        self.part_types = part_types

        all_processes = [] # list for storing all factory processes
        crit_time_dict = {} # dictionary for storing simulator critical times

        # intialize above lists/dictionaries
        for part in part_types:
            crit_time_dict[part] = 0
            for process in part.process_stations:
                if process not in all_processes:
                    all_processes.append(process)
                    crit_time_dict[process] = 0
        self.all_processes = all_processes 
        self.crit_time_dict = crit_time_dict

        self.iterations = 0

    def update_factory(self, prod_time):
        '''Update the factory for current critical time: update process or incoming 
            part buffer for critical time.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        # identify critical time process/part
        crit_obj = self.find_crit_time_object(prod_time)

        # if part type, add part to first process buffer
        if isinstance(crit_obj, PartType):
            crit_obj.add_arriving_part(prod_time)
            crit_obj.process_stations[0].start_process(prod_time)           

        update_count = 1
        while update_count > 0:
            update_count = 0
            for process in self.all_processes:
                part = process.part_in_process
                if part is not None and process.next_crit_time <= prod_time:
                        update_count += part.end_process(process)

                update_count += process.start_process(prod_time)

        # if part type, add part to first process buffer
        self.update_crit_time_dict()

    def initialize_production(self):
        '''Initialize first processes with a part after factory creation. 
            Must run this before running update_factory() for first time.'''

        for part in self.part_types:
            part.add_arriving_part(0)

        self.update_crit_time_dict()

    def find_crit_time_object(self, prod_time):
        '''Find the critical time process at current production time.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.

        Returns:
            Process or PartType object or None: returns critical time process or part, 
                or None if not found.'''

        for process in self.crit_time_dict:
            if self.crit_time_dict[process] == prod_time:
                return process

        return None
            

    def update_crit_time_dict(self):
        '''Update the crit_time_dict for all processes.
        '''

        for process in self.crit_time_dict:
            self.crit_time_dict[process] = process.next_crit_time

    def get_next_crit_time(self):
        '''Retrieve the next critical time from the crit_time_dict, 
            assuming critical time is > 0.
        '''
        self.iterations += 1

        times = [time for time in self.crit_time_dict.values() if time > 0]
        return min(times)
