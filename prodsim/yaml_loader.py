'''Method for loading yaml file into prodsim class objects.'''
import yaml
import argparse
import os
from prodsim.prod_objects import Process, Factory, PartType, ProductionLine


def yaml_loader(input_file):
    '''Load yaml file into factory simulation objects.

        Arguments:
            input_file (.yaml file): .yaml file detailing factory 
                specifications/information 

        Returns:
            factory_object (Factory class object): instance of Factory class 
                describing factory according to input file
            sim_time (scalar): simulation time in consistent units specified 
                in input file
        '''

    with open(input_file) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

        processes_input = data['processes']
        production_lines_input = data['production_lines']
        sim_time = data['simulation_time']

        process_objects = []
        for process in processes_input:
            process_name = process['name']
            process_dist = process['distribution']
            process_params = process['parameters']
            process_buffer = process['buffer_size']
            process_instance = Process(
                process_name, process_dist, process_params, process_buffer)
            process_objects.append(process_instance)

        process_dict = {} # map process name to object
        for process in process_objects:
            process_dict[process.name] = process

        prod_line_objects = []
        for line in production_lines_input:
            part_type_name = line['line_part_type']
            part_arrival_dist = line['part_arrival_distribution']
            part_arrival_params = line['part_arrival_parameters']
            process_name_list = line['process_list']

            process_list = []
            for name in process_name_list:
                process_list.append(process_dict[name])

            part_type_inst = PartType(
                part_type_name, part_arrival_dist, part_arrival_params)
            prod_line_inst = ProductionLine(
                part_type_inst, process_list)
            prod_line_objects.append(prod_line_inst)

        factory_object = Factory(prod_line_objects)

        return factory_object, sim_time

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load .yaml file.')
    parser.add_argument('yaml_file', help='Simlation information input (.yaml) file.')
    args = parser.parse_args()
    yaml_loader(args.yaml_file)