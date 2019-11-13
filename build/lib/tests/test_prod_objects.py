import unittest 

from prodsim.prod_objects import Process

class TestProcessMethods(unittest.TestCase):

    def setUp(self):
        self.process_instance = Process(
            'test', 'uniform', {'low': 2, 'high': 4}, 5)

    def test_process_attributes(self):
        self.assertTrue(self.process_instance.name == 'test')

    def test_process_time(self):
        process_time = self.process_instance.get_process_time()
        self.assertTrue(2 <= process_time < 4)


if __name__ == '__main__':
    unittest.main()