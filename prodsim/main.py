"""Main processing script for prodsim"""
import argparse
import os
from prodsim.yaml_loader import yaml_loader

def main(args):

    factory, sim_time = yaml_loader(args.yaml_file)
    factory.initialize_prod_lines()
    prod_time = factory.get_next_crit_time()

    while prod_time < sim_time:

        print('prod_time: ' + str(prod_time))
        print(factory.crit_time_dict)

        factory.update_factory(prod_time)
        prod_time = factory.get_next_crit_time()
        
    for line in factory.prod_lines:
        print(line.part_type.name + ' throughput: ' + str(line.throughput))




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simulate factory.')
    parser.add_argument('yaml_file', help='Simlation information input (.yaml) file.')
    args = parser.parse_args()
    main(args)