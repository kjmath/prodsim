"""Main processing script for prod-sim"""
#import statements here
import argparse
import os

def main(args):

    pass

    """ make part types
        make process stations
        make production lines
        make factory
        establish total simulation time (sim_time)

        factory, sim_time = yaml_loader(args[1])

        factory_time = 0 # initialize factory time at 0

        while factory_time < sim_time:

            factory.update_factory(prod_time)
            prod_time = factory.get_next_crit_time()
        """


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simulate factory.')
    parser.add_argument('yaml_file', help='Simlation information input (.yaml) file.')
    args = parser.parse_args()
    main(args)