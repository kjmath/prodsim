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
            buffer_cap(scalar or None): maximum buffer capacity AFTER the process station, 
                use None for infinite buffer.

        '''
        self.name = name
        self.prob_dist = prob_dist 
        self.params = params 
        self.buffer_cap = buffer_cap 
        self.buffer_size = 0 # initialize buffer as empty
        self.process_completion_time = 0 # initialize time of next completed process

    def get_process_time(self):
        '''Get process time for next process from probability distribution.

        Returns:
            scalar: process time [units: simulator time units].
        '''

        prob_dist_func = getattr(np.random, self.prob_dist)
        process_time = prob_dist_func(**self.params)
        return process_time

    def update_completion_time(self, process_time, prod_time):
        ''' Update the process_completion_time attribute.

        Arguments:
            process_time (scalar): process time, probably retrieved from get_process_time().
            prod_time (scalar): current production/factory time of the simulation.
        '''

        self.process_completion_time = process_time + prod_time

    def is_buffer_full(self):
        '''Check if buffer AFTER process is full.

        Returns:
            boolean: True if buffer is full, False otherwise.
        '''

        if self.buffer_cap == None:
            return False
        elif self.buffer_size < self.buffer_cap:
            return False
        else:
            return True

    def increment_buffer(self):
        '''Increase buffer size by one.'''

        self.buffer_size += 1

    def decrement_buffer(self):
        '''Decrease buffer size by one.'''

        self.buffer_size -= 1


class Factory:

    def __init__(self, prod_lines):

        self.prod_lines = prod_lines

        processes = []
        for line in prod_lines:
            pass


