"""Collection of classes for prod-sim"""
import numpy as np
from helpers import weibull

"""
Change critical time on the fly--every time a part is finihsed, re-allocate workers

New crit time = (old crit time-prod time) * old number of workers / new number of workers

Need to link workers and processes -- update each time job is finished
    minimize idle workers

Assign workers to processes, not job.

Make dictionary for workers--> process, maybe also process--> workers

Change yaml loader to 
    have second part type
    HD vs LD arguement parameters

Have worker class
    -name
    -job
    -skill level (or list of processes it can do)

Factory has
    list of worker objects
    list of processes
    maps workers to proc and back
    passes Number of workers into process as an arguemnt
        process then scales critical time accordingly
    MAKE SURE that we don't exceed 3 workers per process
    
Attrubite that keeps track of which partIndex a worker is assigned to.

Whenever worker moves, update time dictionary

Add worker inputs to yaml (make  max workers in yaml)
"""



class Process:

    def __init__(self, name, prob_dist, params, buffer_cap, max_parts = 1, max_workers = 1):
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
            max_parts (scalar or None): maximum number of parts that can be processed 
                simulaneously.
        '''
        self.name = name
        self.prob_dist = prob_dist 
        self.params = params 
        self.buffer_cap = buffer_cap 
        self.max_parts = max_parts
        self.max_workers = max_workers
        self.parts_in_process = max_parts * [None] # list containing instances of PartType in process, or None
        self.parts_in_buffer = [] # list of PartType instances in buffer, index 0 is first in line
        self.next_crit_time = max_parts * [0] # initialize times of next completed processes        

    def __str__(self):
        return "{} with {} in process and {} in buffer".format(self.name, len(self.parts_in_process), len(self.parts_in_buffer))


    def start_process(self, prod_time, num_workers = 1):
        '''Start the process: update completion time, move first part in buffer
            to in process.'''
        if None in self.parts_in_process and num_workers > 0:
            part_index = next(ind for ind, val in enumerate(self.parts_in_process) if val is None)

            if self.parts_in_buffer:
                self.update_next_crit_time(prod_time, part_index, num_workers)
                self.parts_in_process[part_index] = self.parts_in_buffer[0]
                self.remove_first_in_buffer()
                return True
            else:
                # set to 0 so simulator can move forward and try again on next iteration
                # print('no parts in buffer')
                self.next_crit_time[part_index] = 0 

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

    def update_next_crit_time(self, prod_time, part_index, num_workers = 1):
        ''' Update the next_crit_time attribute.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
            part_index (scalar): index in parts_in_process list of relevant part
        '''
        if num_workers > 0:
            self.next_crit_time[part_index] = self.get_next_crit_time() / num_workers + prod_time 
        else:
            print("No workers!")


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
        self.next_crit_time = [0]
        self.num_arrivals = 0
        self.throughput = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

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

        self.next_crit_time = [self.get_next_crit_time() + prod_time]

    def end_process(self, process, part_index):
        '''End a process and updates next process buffer, assuming process currently has 
            an in-process part moving in the current production line.

        Arguments:
            process (Process class object): process to be ended. 
            part_index (scalar): index of part in parts_in_process list to be ended.

        Returns:
            boolean: True if process ended, False if not
        '''
        
        if process in self.process_stations and process.parts_in_process[part_index] == self:
            proc_index = self.process_stations.index(process)

            # process is last process
            if proc_index == len(self.process_stations) - 1:
                process.parts_in_process[part_index] = None
                process.next_crit_time[part_index] = 0
                self.throughput += 1
                return True
            # process is not last process and next process has room in buffer
            elif not self.process_stations[proc_index + 1].is_buffer_full():
                process.parts_in_process[part_index] = None
                process.next_crit_time[part_index] = 0
                self.process_stations[proc_index + 1].add_to_buffer(self)
                return True

        process.next_crit_time[part_index] = 0 # set to 0 so simulator can try ending on next critical time
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

class Worker:
    def __init__(self, name, skills, task = None, idleTime = 0):
        """ Initializes a single worker.
        Arguments:
            name: worker's name
            skills: list of process names (not objects) worker can do
            task: worker's current job. None if idle.
            idleTime: a counter that stores idle time.
        """
        self.skills = skills
        self.name = name
        self.task = task
        self.idleTime = idleTime
        self.part = None

    def __str__(self):
        return 'Worker with name: {} and skills: {} is currently working on {} process and {} part'.format(self.name, self.skills, self.task, self.part)
    def is_idle(self):
        if self.task == None:
            return True
        return False
    def assign_task(self, task):
        '''Assigns worker to a process if the worker can do it'''
        process = task
        if process.name in self.skills:
            self.task = process
            return True
        print(self.name, " cannot do task: ", process.name)
        return False
    def assign_part(self, parts):
        self.part = part
    def can_do(self, process):
        if process.name in self.skills:
            return True
        return False
    def get_name(self):
        return self.name

class Factory:

    def __init__(self, part_types, workers = []):
        '''Create a factory object.

        Arguments:
            part_types (list of ProductionLine objects): list of production 
                lines in factory.
            workers: list of worker objects in factory
        '''

        self.part_types = part_types

        all_processes = [] # list for storing all factory processes
        crit_time_dict = {} # dictionary for storing simulator critical times

        # intialize above lists/dictionaries
        for part in part_types:
            crit_time_dict[part] = [0]
            for process in part.process_stations:
                if process not in all_processes:
                    all_processes.append(process)
                    crit_time_dict[process] = process.max_parts * [0]
        self.all_processes = all_processes 
        self.crit_time_dict = crit_time_dict

        self.iterations = 0
        self.workers = workers
        self.worker_assignments = {} #maps workers to task
        for worker in self.workers:
            self.worker_assignments[worker] = None #initialize to idle workers.
        self.allocate_workers()
        for worker in self.workers:
            print(worker)

    def get_num_workers_on_task(self, task):
        total = 0
        for worker in self.workers:
            if self.worker_assignments[worker] == task:
                total += 1
        return total

    def update_factory(self, prod_time):
        '''Update the factory for current critical time: update process or incoming 
            part buffer for critical time.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.
        '''

        # identify critical time process/part
        crit_obj, crit_index = self.find_crit_time_object(prod_time)
        #print(crit_obj.name)
        #print(prod_time)

        # if part type, add part to first process buffer
        if isinstance(crit_obj, PartType):
            crit_obj.add_arriving_part(prod_time)
            crit_obj.process_stations[0].start_process(prod_time, self.get_num_workers_on_task(crit_obj.process_stations[0]))                      #ADD NUMBER OF WORKERS ON PROCESS HERE
        else:
            pass
            # print(crit_obj.parts_in_process)       

        update_count = 1
        while update_count > 0:
            update_count = 0
            for process in self.all_processes:
                for part_index, part in enumerate(process.parts_in_process):
                    if part is not None and process.next_crit_time[part_index] <= prod_time:
                        update_count += part.end_process(process, part_index)
                        """
                        for worker that is assigned to process
                            worker task = None
                        """

                    update_count += process.start_process(prod_time, self.get_num_workers_on_task(process))

        self.update_crit_time_dict()
        print(self.crit_time_dict)
        self.allocate_workers()
        # print(self.crit_time_dict)
        # print(self.worker_assignments)

    def initialize_production(self):
        '''Initialize first processes with a part after factory creation. 
            Must run this before running update_factory() for first time.'''
        print("Production Initialized")
        for part in self.part_types:
            part.add_arriving_part(0)
        for process in self.all_processes:
            print(process)
        self.allocate_workers()
        self.update_crit_time_dict()

    def find_crit_time_object(self, prod_time):
        '''Find the critical time process at current production time.

        Arguments:
            prod_time (scalar): current production/factory time of the simulation.

        Returns:
            Process or PartType: returns critical time process or part.
            Part Index: returns part index of critical time proces,
                or None if not found.'''

        for process in self.crit_time_dict:
            for part_index, time in enumerate(self.crit_time_dict[process]):
                if time == prod_time:
                    return process, part_index

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

        times = []
        for time_list in self.crit_time_dict.values():
            for time in time_list:
                if time > 0:
                    times.append(time)

        return min(times)

    def allocate_workers(self):
        """
            Should assign idle worker to a task they can do
        """
        #print("Allocating workers___________________________________________________________________________________")
        
        for worker in self.workers:
            if worker.task is None: #Worker not assigned a process
                for process in self.all_processes:
                    if worker.can_do(process): # If this is something we can do
                        if process.parts_in_buffer or process.parts_in_process:
                            worker.assign_task(process)
                            self.worker_assignments[worker] = (process, None)

            #elif worker.part is None: #Worker has a process but no part

        # for process in self.all_processes:
        #     for part_index in range(process.max_parts):
        #         print("finding wokrers for: ", process.name)
        #         for worker in self.workers:
        #             if (self.worker_assignments[worker] is None):
        #                 print("Idle worker found, attempting to assign ", worker)

        #                 (process.parts_in_process[part_index] is not None or process.parts_in_buffer):# or 
        #                 #len(worker.skills) is 1):
        #                 print("Idle worker found, attempting to assign")
        #                 if worker.can_do(process.name):
        #                     print("found a match! assigning worker to : ", process.name)
        #                     self.worker_assignments[worker] = (process, part_index)
        #                     worker.assign_task((process, part_index))
