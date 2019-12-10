"""Main processing script for prodsim"""
import argparse
import os
from yaml_loader import yaml_loader

def main(args):

    factory, sim_time = yaml_loader(args.yaml_file) # load simulation specs
    print("Initializing Factory")
    factory.initialize_production() # intialize first process buffers
    prod_time = factory.get_next_crit_time() # initialize factory time

    while prod_time < sim_time:

        print(prod_time)

        factory.update_factory(prod_time)
        prod_time = factory.get_next_crit_time()
        
    print('Final production time: ' + str(prod_time))
    print('Number of iterations: ' + str(factory.iterations))    

    for part in factory.part_types:
        print(part.name + ' throughput: ' + str(part.throughput))
        print(part.name + ' arrivals: ' + str(part.num_arrivals))
        
        for process in part.process_stations:
            print('buffer size of ' + str(process.name) + ': ' + str(len(process.parts_in_buffer)))

    #for worker in factory.workers:
    #    print(worker)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simulate factory.')
    parser.add_argument('yaml_file', help='Simlation information input (.yaml) file.')
    args = parser.parse_args()
    main(args)
