'''Test cases for classes in prod_objects.py.'''

import unittest
import numpy as np

from prodsim.prod_objects import Process, Factory, PartType, ProductionLine

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

    def test_start_process1(self):
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
        self.assertFalse(self.process_instance.is_buffer_full())
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


class TestPartTypeMethods(unittest.TestCase):
    '''Test cases for PartType class.'''

    def setUp(self):
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5})

    def test_get_part_arrival_time(self):
        '''Test PartType.get_part_arrival_time() method.'''
        arrival_time = self.part_type_inst1.get_part_arrival_time()
        self.assertTrue(1 <= arrival_time < 5)

    def test_update_part_arrival_time(self):
        '''Test PartType.updage_part_arrival_time() method.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=1, high=5)
        np.random.seed(0)
        self.part_type_inst1.update_part_arrival_time(sample_prod_time)
        self.assertTrue(self.part_type_inst1.part_arrival_time 
                        == sample_prod_time + pt)


class TestProductionLineMethods(unittest.TestCase):
    '''Test cases for ProductionLine class.'''

    def setUp(self):
        self.process_instance1 = Process(
            'test1', 'uniform', {'low': 2, 'high': 4}, 3)
        self.process_instance2 = Process(
            'test2', 'uniform', {'low': 2, 'high': 4}, 3)
        self.process_instance3 = Process(
            'test3', 'uniform', {'low': 2, 'high': 4}, 1)
        self.process_list = [self.process_instance1, self.process_instance2, 
                        self.process_instance3]
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5})
        self.prod_line1 = ProductionLine(self.part_type_inst1, 
                                         self.process_list)

    def test_production_line_init(self):
        '''Test ProductionLine.__init__() method.'''
        self.assertTrue(self.prod_line1.process_stations == 
                        self.process_list)
        self.assertTrue(self.prod_line1.part_type == 
                        self.part_type_inst1)

    def test_end_process1(self):
        '''Test ProductionLine.end_process() method with correct part 
            in processs2 and empty buffer for process3.'''
        self.process_instance2.part_in_process = self.part_type_inst1
        self.prod_line1.end_process(self.process_instance2)
        self.assertIsNone(self.process_instance2.part_in_process)
        self.assertTrue(self.process_instance3.parts_in_buffer == 
                        [self.part_type_inst1])

    def test_end_process2(self):
        '''Test ProductionLine.end_process() method with correct part
            in process2 and full buffer for process3.'''
        self.process_instance2.part_in_process = self.part_type_inst1
        self.process_instance3.add_to_buffer(self.part_type_inst1)
        self.prod_line1.end_process(self.process_instance2)
        self.assertTrue(self.process_instance2.part_in_process == 
                        self.part_type_inst1)
        self.assertTrue(self.process_instance3.parts_in_buffer == 
                        [self.part_type_inst1])

    def test_end_process3(self):
        '''Test Production.end_process() method with correct part
            in process3, where process3 is the final process.'''
        self.process_instance3.part_in_process = self.part_type_inst1
        self.prod_line1.end_process(self.process_instance3)
        self.assertIsNone(self.process_instance3.part_in_process)

    def test_end_process4(self):
        '''Test Production.end_process() method with incorrect part
            in process2, and empty buffer for process3.'''
        part_type_inst2 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5})
        self.process_instance2.part_in_process = part_type_inst2
        self.prod_line1.end_process(self.process_instance2)
        self.assertTrue(self.process_instance2.part_in_process == 
                        part_type_inst2)
        self.assertTrue(not self.process_instance3.parts_in_buffer)

class TestFactoryMethods(unittest.TestCase):
    '''Test cases for Factory class.'''

    def setUp(self):
        self.process_instance1 = Process(
            'test1', 'uniform', {'low': 2, 'high': 4}, 3)
        self.process_instance2 = Process(
            'test2', 'uniform', {'low': 2, 'high': 4}, 3)
        self.process_instance3 = Process(
            'test3', 'uniform', {'low': 2, 'high': 4}, 1)
        self.process_instance4 = Process(
            'test4', 'uniform', {'low': 2, 'high': 4}, 1)
        self.process_list1 = [self.process_instance1, self.process_instance2, 
                              self.process_instance3]
        self.process_list2 = [self.process_instance1, self.process_instance2, 
                              self.process_instance4]
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5})
        self.part_type_inst2 = PartType(
            'test_part2', 'uniform', {'low': 1, 'high': 5})
        self.prod_line1 = ProductionLine(self.part_type_inst1, 
                                         self.process_list1)
        self.prod_line2 = ProductionLine(self.part_type_inst2,
                                         self.process_list2)
        self.prod_line_list = [self.prod_line1, self.prod_line2]
        self.factory = Factory(self.prod_line_list)

    def test_factory_init1(self):
        '''Test Factory.__init__() prod_lines attribute.'''
        self.assertTrue(self.factory.prod_lines == self.prod_line_list)

    def test_factory_init2(self):
        '''Test Factory.__init__() all_process attribute.'''
        test_process_list = [self.process_instance4, self.process_instance1, 
                             self.process_instance3, self.process_instance2]
        self.assertTrue(set(self.factory.all_processes) == 
                        set(test_process_list))

    def test_factory_init3(self):
        '''Test Factory.__init__() crit_time_dict attribute.'''
        test_crit_time_dict = {self.part_type_inst1: -1, self.part_type_inst2: -1,
                               self.process_instance1: -1, self.process_instance2: -1,
                               self.process_instance3: -1, self.process_instance4: -1}
        self.assertTrue(self.factory.crit_time_dict ==
                        test_crit_time_dict)

    def test_factory_init4(self):
        '''Test Factory.__init__() buffer_full_dict attribute.'''
        test_buffer_full_dict = {self.process_instance1: False, self.process_instance2: False,
                                 self.process_instance3: False, self.process_instance4: False}
        self.assertTrue(self.factory.buffer_full_dict ==
                        test_buffer_full_dict)

    def test_factory_init5(self):
        '''Test Factory.__init__() part_type_list attribute.'''
        test_part_type_list = [self.part_type_inst2, self.part_type_inst1]
        self.assertTrue(set(self.factory.part_type_list) ==
                        set(test_part_type_list))

    def test_find_crit_time_process1(self):
        '''Test Factory.find_crit_time_process() for a critical time in dictionary.'''
        self.factory.crit_time_dict[self.process_instance3] = 5
        sample_prod_time = 5
        self.assertTrue(self.factory.find_crit_time_process(sample_prod_time) ==
                        self.process_instance3)

    def test_find_crit_time_process2(self):
        '''Test Factory.find_crit_time_process() for no critical time in dictionary.'''
        sample_prod_time = 5
        self.assertIsNone(self.factory.find_crit_time_process(sample_prod_time))


if __name__ == '__main__':
    unittest.main(verbosity=2)
