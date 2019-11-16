"""Main processing script for prodsim"""
import argparse
import os

def main(args):

    pass

    """ make part types
        make process stations
        make production lines
        make factory
        establish total simulation time (sim_time)
        deal with startup (run PartType.add_arriving_part() for each part)
        maybe choose min next crit time for crit time > 0

        factory, sim_time = yaml_loader(args[1])

        prod_time = 0 # initialize factory time at 0

        factory.initialize_prod_lines(prod_time)

        while prod_time < sim_time:

            factory.update_factory(prod_time)
            prod_time = factory.get_next_crit_time()
        """


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Simulate factory.')
    parser.add_argument('yaml_file', help='Simlation information input (.yaml) file.')
    args = parser.parse_args()
    main(args)