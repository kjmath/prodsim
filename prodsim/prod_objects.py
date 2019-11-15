"""Collection of classes for prod-sim"""
import numpy as np

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
        '''start the process: update completion time, move first part in buffer
            to in process.'''

        if self.part_in_process is None:
            if self.parts_in_buffer:
                self.update_next_crit_time(prod_time)
                self.part_in_process = self.parts_in_buffer[0]
                self.remove_first_in_buffer()
                return True

        return False


    def get_next_crit_time(self):
        '''Get process time for next process from probability distribution.

        Returns:
            scalar: process time [units: simulator time units].
        '''

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
        self.next_crit_time = 0

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


class ProductionLine:

    def __init__(self, part_type, process_stations):
        '''Create a production line object.

        Arguments:
            part_type (PartType class object): part type instance corresponding to the part type
                of the production line.
            process_stations (list): ordered list of Process objects representing the
                production line for the designated part type. 
        '''

        self.part_type = part_type
        self.process_stations = process_stations

    def end_process(self, process):
        '''End a process and updates next process buffer, assuming process currently has 
            an in-process part moving in the current production line.

        Arguments:
            process (Process class object): process to be ended. 
        '''

        if process.part_in_process == self.part_type:
        
            proc_index = self.process_stations.index(process)

            if proc_index == len(self.process_stations) - 1:
                process.part_in_process = None
            elif not self.process_stations[proc_index + 1].is_buffer_full():
                process.part_in_process = None
                self.process_stations[proc_index + 1].add_to_buffer(self.part_type)

    def add_arriving_part(self, prod_time):
        '''Add an arriving part to the buffer of the first process in the production line, 
            assuming the buffer is not full. Update next critical time.
        
        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        first_process = self.process_stations[0]

        if not first_process.is_buffer_full():
            first_process.add_to_buffer(self.part_type)

        self.part_type.update_next_crit_time(prod_time)


class Factory:

    def __init__(self, prod_lines):
        '''Create a factory object.

        Arguments:
            prod_lines (list of ProductionLine objects): list of production 
                lines in factory.
        '''

        self.prod_lines = prod_lines

        all_processes = [] # list for storing all factory processes
        crit_time_dict = {} # dictionary for storing simulator critical times
        buffer_full_dict = {} # dictionary for storing processes with full buffers
        part_type_dict = {} # dictionary for mapping part types to production lines

        # intialize above lists/dictionaries
        for line in prod_lines:
            part_type_dict[line.part_type] = line
            crit_time_dict[line.part_type] = 0
            for process in line.process_stations:
                if process not in all_processes:
                    all_processes.append(process)
                    crit_time_dict[process] = 0
                    buffer_full_dict[process] = False
        self.all_processes = all_processes # TODO not sure if needed
        self.crit_time_dict = crit_time_dict
        self.buffer_full_dict = buffer_full_dict # TODO not sure if needed
        self.part_type_dict = part_type_dict

    def update_factory(self, prod_time):
        '''Update the factory for current critical time: update process or incoming 
            part buffer for critical time.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        # identify critical time process/part
        crit_obj = self.find_crit_time_object()
        cycle = False

        # if process, end and restart process
        if isinstance(crit_obj, Process):
            cycle = crit_obj.is_buffer_full()
            crit_part = crit_obj.part_in_process
            crit_prod_line = self.part_type_dict[crit_part]
            crit_prod_line.end_process(crit_obj)
            crit_obj.start_process(prod_time)

        # if part type, add part to first process buffer
        elif isinstance(crit_obj, PartType):
            crit_prod_line = self.part_type_dict[crit_obj]
            crit_prod_line.add_arriving_part(prod_time)

        # if critical time process had a full buffer, it may have been 
        # preventing other processes from progressing; end/restart all processes
        # if this is the case.
        if cycle:
            update_count = 1
            while update_count > 0:
                update_count = 0
                for process in self.all_processes:
                    part = process.part_in_process
                    prod_line = self.part_type_dict[part]
                    prod_line.end_process(process)
                    update_count += process.start_process()

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
        '''Retrieve the next critical time from the crit_time_dict, only
            considering values greater than 0.'''

        greater0 = [time for time in self.crit_time_dict.values() if time > 0]
        return min(greater0)
