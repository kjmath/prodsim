'''Test cases for methods in yaml_loader.py.'''

import os
import unittest
from prodsim.yaml_loader import yaml_loader

class TestYamlLoader(unittest.TestCase):
    '''Test cases for yaml_loader.py method.'''

    def test_yaml_loader(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_file_path = os.path.join(test_dir, 'test_factory.yaml')
        factory, sim_time = yaml_loader(test_file_path)
        self.assertTrue(sim_time == 30)
        self.assertTrue(factory.part_types[0].process_stations[0].buffer_cap == 3)
        self.assertTrue(len(factory.all_processes) == 4)

if __name__ == '__main__':
    unittest.main(verbosity=2)