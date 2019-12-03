'''Test cases for classes in prod_objects.py.'''

import unittest
import numpy as np
import copy

from prodsim.prod_objects import Process, Factory, PartType


class TestProcessMethods(unittest.TestCase):
    '''Test cases for Process class.'''

    def setUp(self):
        self.process_instance = Process(
            'test', 'uniform', {'low': 2, 'high': 4}, 3, 1)
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5}, [self.process_instance])
        self.part_type_inst2 = PartType(
            'test_part2', 'uniform', {'low': 1, 'high': 5}, [self.process_instance])
        self.part_type_inst3 = PartType(
            'test_part3', 'uniform', {'low': 1, 'high': 5}, [self.process_instance])

    def test_process_init(self):
        '''Test Process.__init__() method.'''
        self.assertTrue(self.process_instance.name == 'test')
        self.assertTrue(self.process_instance.prob_dist == 'uniform')

    def test_start_process1(self):
        '''Test Process.start_process() method, with no part in 
            process and empty buffer.'''
        sample_prod_time = 5
        self.process_instance.start_process(sample_prod_time)
        self.assertTrue(self.process_instance.parts_in_process == self.process_instance.max_parts * [None])
        self.assertTrue(self.process_instance.next_crit_time == self.process_instance.max_parts * [0])
        self.assertTrue(not self.process_instance.parts_in_buffer)

    def test_start_process2(self):
        '''Test Process.start_process() method, with a part in 
            process and empty buffer.'''
        sample_prod_time = 5

        self.process_instance.parts_in_process[0] = self.part_type_inst1
        self.process_instance.start_process(sample_prod_time)

        test_parts = self.process_instance.max_parts * [None]
        test_parts[0] = self.part_type_inst1

        self.assertTrue(self.process_instance.parts_in_process == 
                        test_parts)
        self.assertTrue(self.process_instance.next_crit_time == 
                        self.process_instance.max_parts * [0])
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

        test_parts = self.process_instance.max_parts * [None]
        test_parts[0] = self.part_type_inst1
        self.assertTrue(self.process_instance.parts_in_process == test_parts)

        test_crit_time = self.process_instance.max_parts * [0]
        test_crit_time[0] = sample_prod_time + pt
        self.assertTrue(self.process_instance.next_crit_time == test_crit_time)

        self.assertTrue(self.process_instance.parts_in_buffer ==
                        [self.part_type_inst2, self.part_type_inst3])

    def test_get_next_crit_time(self):
        '''Test Process.get_next_crit_time() method.'''
        process_time = self.process_instance.get_next_crit_time()
        self.assertTrue(2 <= process_time < 4)

    def test_update_next_crit_time(self):
        '''Test Process.update_next_crit_time() method.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=2, high=4)
        test_update_time = self.process_instance.max_parts * [0]
        test_update_time[0] = sample_prod_time + pt
        np.random.seed(0)
        self.process_instance.update_next_crit_time(sample_prod_time, 0)
        self.assertTrue(self.process_instance.next_crit_time 
                        == test_update_time)

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
        self.process_instance1 = Process(
            'test1', 'uniform', {'low': 2, 'high': 4}, 1, 1)
        self.process_instance2 = Process(
            'test2', 'uniform', {'low': 2, 'high': 4}, 3, 1)
        self.process_instance3 = Process(
            'test3', 'uniform', {'low': 2, 'high': 4}, 1, 1)
        self.process_list = [self.process_instance1, self.process_instance2, 
                             self.process_instance3]
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5}, self.process_list)

    def test_part_type_init(self):
        '''Test PartType.__init__() method.'''
        self.assertTrue(self.part_type_inst1.process_stations == 
                        self.process_list)
        self.assertTrue(self.part_type_inst1.arrival_prob_dist == 
                        'uniform')

    def test_get_next_crit_time(self):
        '''Test PartType.get_next_crit_time() method.'''
        arrival_time = self.part_type_inst1.get_next_crit_time()
        self.assertTrue(1 <= arrival_time < 5)

    def test_update_next_crit_time(self):
        '''Test PartType.updage_next_crit_time() method.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=1, high=5)
        np.random.seed(0)
        self.part_type_inst1.update_next_crit_time(sample_prod_time)
        self.assertTrue(self.part_type_inst1.next_crit_time 
                        == [sample_prod_time + pt])

    def test_end_process1(self):
        '''Test PartType.end_process() method with correct part 
            in processs2 and empty buffer for process3.'''
        self.process_instance2.parts_in_process[0] = self.part_type_inst1
        self.part_type_inst1.end_process(self.process_instance2, 0)
        self.assertTrue(self.process_instance2.parts_in_process ==
                        self.process_instance2.max_parts * [None])
        self.assertTrue(self.process_instance3.parts_in_buffer == 
                        [self.part_type_inst1])

    def test_end_process2(self):
        '''Test PartType.end_process() method with correct part
            in process2 and full buffer for process3.'''
        self.process_instance2.parts_in_process[0] = self.part_type_inst1
        self.process_instance3.add_to_buffer(self.part_type_inst1)
        self.part_type_inst1.end_process(self.process_instance2, 0)

        test_parts = self.process_instance2.max_parts * [None]
        test_parts[0] = self.part_type_inst1
        self.assertTrue(self.process_instance2.parts_in_process == 
                        test_parts)
        self.assertTrue(self.process_instance3.parts_in_buffer == 
                        [self.part_type_inst1])

    def test_end_process3(self):
        '''Test PartType.end_process() method with correct part
            in process3, where process3 is the final process.'''
        self.process_instance3.parts_in_process[0] = self.part_type_inst1
        self.part_type_inst1.end_process(self.process_instance3, 0)
        self.assertTrue(self.process_instance3.parts_in_process ==
                        self.process_instance3.max_parts * [None])

    def test_end_process4(self):
        '''Test PartType.end_process() method with incorrect part
            in process2, and empty buffer for process3.'''
        part_type_inst2 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5}, self.process_list)
        self.process_instance2.parts_in_process[0] = part_type_inst2
        self.part_type_inst1.end_process(self.process_instance2, 0)

        test_parts = self.process_instance2.max_parts * [None]
        test_parts[0] = part_type_inst2
        self.assertTrue(self.process_instance2.parts_in_process == test_parts)
        self.assertTrue(not self.process_instance3.parts_in_buffer)

    def test_add_arriving_part1(self):
        '''Test PartType.add_arriving_part() method with empty first
            process buffer.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=1, high=5)
        np.random.seed(0)    
        self.part_type_inst1.add_arriving_part(sample_prod_time)

        test_crit_time = self.part_type_inst1.process_stations[0].max_parts * [0]
        test_crit_time[0] = sample_prod_time + pt
        self.assertTrue(self.part_type_inst1.next_crit_time == test_crit_time)

        test_parts = self.part_type_inst1.process_stations[0].max_parts * [None]
        test_parts[0] = self.part_type_inst1
        self.assertTrue(self.part_type_inst1.process_stations[0].parts_in_buffer ==
                        test_parts)

    def test_add_arriving_part2(self):
        '''Test PartType.add_arriving_part() method with full first
            process buffer.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=1, high=5)
        np.random.seed(0)
        part_type_inst2 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5}, self.process_list)
        self.process_instance1.add_to_buffer(part_type_inst2)
        self.part_type_inst1.add_arriving_part(sample_prod_time)
        self.assertTrue(self.part_type_inst1.next_crit_time 
                        == [sample_prod_time + pt])
        self.assertTrue(self.part_type_inst1.process_stations[0].parts_in_buffer ==
                        [part_type_inst2])


class TestFactoryMethods(unittest.TestCase):
    '''Test cases for Factory class.'''

    def setUp(self):
        self.process_instance1 = Process(
            'test1', 'uniform', {'low': 2, 'high': 4}, 3, 1)
        self.process_instance2 = Process(
            'test2', 'uniform', {'low': 2, 'high': 4}, 3, 1)
        self.process_instance3 = Process(
            'test3', 'uniform', {'low': 2, 'high': 4}, 1, 1)
        self.process_instance4 = Process(
            'test4', 'uniform', {'low': 2, 'high': 4}, 1, 1)
        self.process_list1 = [self.process_instance1, self.process_instance2, 
                              self.process_instance3]
        self.process_list2 = [self.process_instance1, self.process_instance2, 
                              self.process_instance4]
        self.part_type_inst1 = PartType(
            'test_part1', 'uniform', {'low': 1, 'high': 5}, self.process_list1)
        self.part_type_inst2 = PartType(
            'test_part2', 'uniform', {'low': 1, 'high': 5}, self.process_list2)
        self.part_type_list = [self.part_type_inst1, self.part_type_inst2]
        self.factory = Factory(self.part_type_list)

    def test_factory_init1(self):
        '''Test Factory.__init__() part_types attribute.'''
        self.assertTrue(self.factory.part_types == self.part_type_list)

    def test_factory_init2(self):
        '''Test Factory.__init__() all_process attribute.'''
        test_process_list = [self.process_instance4, self.process_instance1, 
                             self.process_instance3, self.process_instance2]
        self.assertTrue(set(self.factory.all_processes) == 
                        set(test_process_list))

    def test_factory_init3(self):
        '''Test Factory.__init__() crit_time_dict attribute.'''
        test_crit_time_dict = {self.part_type_inst1: [0], self.part_type_inst2: [0],
                               self.process_instance1: self.process_instance1.max_parts * [0],
                               self.process_instance2: self.process_instance2.max_parts * [0],
                               self.process_instance3: self.process_instance3.max_parts * [0],
                               self.process_instance4: self.process_instance4.max_parts * [0]}
        self.assertTrue(self.factory.crit_time_dict ==
                        test_crit_time_dict)

    def test_find_crit_time_object1(self):
        '''Test Factory.find_crit_time_object() for a critical time in dictionary.'''
        self.factory.crit_time_dict[self.process_instance3][0] = 5
        sample_prod_time = 5
        self.assertTrue(self.factory.find_crit_time_object(sample_prod_time) ==
                        (self.process_instance3, 0))

    def test_find_crit_time_object2(self):
        '''Test Factory.find_crit_time_object() for no critical time in dictionary.'''
        sample_prod_time = 5
        self.assertIsNone(self.factory.find_crit_time_object(sample_prod_time))

    def test_update_crit_time_dict(self):
        '''Test Factory.update_crit_time_dict() method.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt = np.random.uniform(low=1, high=5)
        np.random.seed(0)
        self.part_type_inst1.update_next_crit_time(sample_prod_time)
        self.factory.update_crit_time_dict()
        test_crit_time_dict = {self.part_type_inst1: [sample_prod_time + pt], 
                               self.part_type_inst2: [0], self.process_instance1: [0], 
                               self.process_instance2: [0], self.process_instance3: [0],
                               self.process_instance4: [0]}
        self.assertTrue(self.factory.crit_time_dict ==
                        test_crit_time_dict)

    def test_get_next_crit_time1(self):
        '''Test Factory.get_next_crit_time() method, with one > 0 value in dict.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt1 = np.random.uniform(low=1, high=5) + sample_prod_time
        np.random.seed(0)
        self.part_type_inst1.update_next_crit_time(sample_prod_time)
        self.factory.update_crit_time_dict()
        self.assertTrue(self.factory.get_next_crit_time() == pt1)
    
    def test_get_next_crit_time2(self):
        '''Test Factory.get_next_crit_time() method, with all values in dict.'''
        sample_prod_time = 5
        np.random.seed(0)
        pt1 = np.random.uniform(low=1, high=5) + sample_prod_time
        pt2 = np.random.uniform(low=1, high=5) + sample_prod_time
        pt3 = np.random.uniform(low=2, high=4) + sample_prod_time
        pt4 = np.random.uniform(low=2, high=4) + sample_prod_time
        pt5 = np.random.uniform(low=2, high=4) + sample_prod_time
        pt6 = np.random.uniform(low=2, high=4) + sample_prod_time
        np.random.seed(0)
        self.part_type_inst1.update_next_crit_time(sample_prod_time)
        self.part_type_inst2.update_next_crit_time(sample_prod_time)
        self.process_instance1.update_next_crit_time(sample_prod_time, 0)
        self.process_instance2.update_next_crit_time(sample_prod_time, 0)
        self.process_instance3.update_next_crit_time(sample_prod_time, 0)
        self.process_instance4.update_next_crit_time(sample_prod_time, 0)
        self.factory.update_crit_time_dict()
        self.assertTrue(self.factory.get_next_crit_time() == min([pt1, pt2, pt3, pt4, pt5, pt6]))

    def test_initialize_prod(self):
        '''Test Factory.initialize_production() method for newly created factory instance.'''
        np.random.seed(0)
        pt1 = np.random.uniform(low=1, high=5)
        pt2 = np.random.uniform(low=1, high=5)
        np.random.seed(0)
        test_crit_time_dict = {self.part_type_inst1: [pt1], self.part_type_inst2: [pt2],
                               self.process_instance1: [0], self.process_instance2: [0],
                               self.process_instance3: [0], self.process_instance4: [0]}
        self.factory.initialize_production()
        self.assertTrue(self.factory.crit_time_dict == test_crit_time_dict)

    def test_update_factory1(self):
        '''Test Factory.update_factory() with > 0 dict elements, empty buffers.'''
        sample_prod_time = 5
        np.random.seed(0)
        self.part_type_inst1.update_next_crit_time(sample_prod_time)
        self.part_type_inst2.update_next_crit_time(sample_prod_time)
        self.process_instance1.update_next_crit_time(sample_prod_time, 0)
        self.process_instance2.update_next_crit_time(sample_prod_time, 0)
        self.process_instance3.update_next_crit_time(sample_prod_time, 0)
        self.process_instance4.update_next_crit_time(sample_prod_time, 0)
        self.factory.update_crit_time_dict()
        check1 = copy.deepcopy(self.factory.crit_time_dict)
        next_prod_time = self.factory.get_next_crit_time()
        self.factory.update_factory(next_prod_time)
        check2 = self.factory.crit_time_dict
        self.assertFalse(check1 == check2)


    def test_update_factory2(self):
        '''Test Factory.update_factory() with newly initialized factory instance.'''
        np.random.seed(0)
        self.factory.initialize_production()
        first_prod_time = self.factory.get_next_crit_time()
        self.assertTrue(self.process_instance1.parts_in_buffer == [self.part_type_inst1, self.part_type_inst2])
        self.factory.update_factory(first_prod_time)
        np.random.seed(0)
        pt1 = np.random.uniform(low=1, high=5)
        pt2 = np.random.uniform(low=1, high=5)
        add = np.random.uniform(low=1, high=5)
        proc_add = np.random.uniform(low=2, high=4) + first_prod_time
        if pt1 < pt2:
            pt1 += add
            self.assertTrue(self.process_instance1.parts_in_process[0] == self.part_type_inst1)
            self.assertTrue(self.process_instance1.parts_in_buffer == [self.part_type_inst2, self.part_type_inst1])
        else:
            pt2 += add
            self.assertTrue(self.process_instance1.parts_in_process[0] == self.part_type_inst2)
            self.assertTrue(self.process_instance1.parts_in_buffer == [self.part_type_inst2, self.part_type_inst2])
        test_crit_time_dict = {self.part_type_inst1: [pt1], self.part_type_inst2: [pt2],
                               self.process_instance1: [proc_add], self.process_instance2: [0],
                               self.process_instance3: [0], self.process_instance4: [0]}
        self.assertTrue(self.factory.crit_time_dict == test_crit_time_dict)


if __name__ == '__main__':
    unittest.main(verbosity=2)
