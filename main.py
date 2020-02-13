import argparse
from simulation import Simulation


def main():
    argparser = argparse.ArgumentParser(
        description='Shipping simulation v1.0')
    argparser.add_argument(
        '--verbose',
        # action='store_true',
        default=0,
        # dest='debug',
        help='Print debug information')
    argparser.add_argument(
        '--NBR_SHIPS',
        default=35,
        help='Number of ships')
    argparser.add_argument(
        '--NBR_PORTS',
        default=10,
        help='Number of ports')
    argparser.add_argument(
        '--NBR_SHIPYARDS',
        default=2,
        help='Number of shipyards')
    argparser.add_argument(
        '--NBR_SHIPOWNERS',
        default=2,
        help='Number of shipowners')
    argparser.add_argument(
        '--NBR_STEPS',
        default=100000,
        help='Number of steps')
    argparser.add_argument(
        '--MAP_SIZE',
        default=600,
        help='Map size: width x height')
    argparser.add_argument(
        '--SIMULATION_TIME',
        default=0.001,
        help='Time of step')
    args = argparser.parse_args()
    shippingSim = Simulation(args)
    is_end_sim = shippingSim.run()
    if is_end_sim:
        print("\nAll steps done. End of simulation")

if __name__ == "__main__":
    main()


