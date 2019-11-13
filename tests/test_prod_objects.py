import unittest
import numpy as np

from prodsim.prod_objects import Process, Factory, PartType

class TestProcessMethods(unittest.TestCase):
    '''Test cases for Process class.'''

    def setUp(self):
        self.process_instance = Process(
            'test', 'uniform', {'low': 2, 'high': 4}, 3)
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5})
        self.part_type_inst2 = PartType(
            'test_part2', 'uniform', {'low': 1, 'high': 5})
        self.part_type_inst3 = PartType(
            'test_part3', 'uniform', {'low': 1, 'high': 5})

    def test_process_init(self):
        '''Test Process.__init__() method.'''
        self.assertTrue(self.process_instance.name == 'test')
        self.assertTrue(self.process_instance.prob_dist == 'uniform')

    def test_start_process(self):
        '''Test Process.start_process() method, with no part in 
            process and empty buffer.'''
        sample_prod_time = 5
        self.process_instance.start_process(sample_prod_time)
        self.assertIsNone(self.process_instance.part_in_process)
        self.assertTrue(self.process_instance.process_completion_time == 0)
        self.assertTrue(not self.process_instance.parts_in_buffer)

    def test_start_process2(self):
        '''Test Process.start_process() method, with a part in 
            process and empty buffer.'''
        sample_prod_time = 5
        self.process_instance.part_in_process = self.part_type_inst1
        self.process_instance.start_process(sample_prod_time)
        self.assertTrue(self.process_instance.part_in_process == 
                        self.part_type_inst1)
        self.assertTrue(self.process_instance.process_completion_time == 0)
        self.assertTrue(not self.process_instance.parts_in_buffer)

    def test_start_process3(self):
        '''Test Process.start_process() method with no part in
            process and parts in buffer.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=2, high=4)
        np.random.seed(0)
        self.process_instance.parts_in_buffer = \
            [self.part_type_inst1, self.part_type_inst2, self.part_type_inst3]
        self.process_instance.start_process(sample_prod_time)
        self.assertTrue(self.process_instance.part_in_process == 
                        self.part_type_inst1)
        self.assertTrue(self.process_instance.process_completion_time 
                        == sample_prod_time + pt)
        self.assertTrue(self.process_instance.parts_in_buffer ==
                        [self.part_type_inst2, self.part_type_inst3])

    def test_process_time(self):
        '''Test Process.get_process_time() method.'''
        process_time = self.process_instance.get_process_time()
        self.assertTrue(2 <= process_time < 4)

    def test_update_completion_time(self):
        '''Test Process.update_completion_time() method.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=2, high=4)
        np.random.seed(0)
        self.process_instance.update_completion_time(sample_prod_time)
        self.assertTrue(self.process_instance.process_completion_time 
                        == sample_prod_time + pt)

    def test_is_buffer_full(self):
        '''Test Process.is_buffer_full() method.'''
        self.process_instance.parts_in_buffer = \
            [self.part_type_inst1, self.part_type_inst2, self.part_type_inst3]
        self.assertTrue(self.process_instance.is_buffer_full())

    def test_add_to_buffer(self):
        '''Test Process.add_to_buffer() method.'''
        self.process_instance.add_to_buffer(self.part_type_inst1)
        self.assertTrue(self.process_instance.parts_in_buffer == 
                        [self.part_type_inst1])

    def test_remove_first_in_buffer(self):
        '''Test Process.remove_first_in_buffer() method.'''
        self.process_instance.parts_in_buffer = \
            [self.part_type_inst1, self.part_type_inst2, self.part_type_inst3]
        self.process_instance.remove_first_in_buffer()
        self.assertTrue(self.process_instance.parts_in_buffer ==
                        [self.part_type_inst2, self.part_type_inst3])


class TestFactoryMethods(unittest.TestCase):

    def setUp(self):
        pass

if __name__ == '__main__':
    unittest.main(verbosity=2)