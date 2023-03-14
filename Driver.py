""" Driver.py """

import simpy

from . import Globals
from . import Simulator
from . import ProgressBar
from . import TraceUtils


def run_sim(M, t, output_dir=None, bar=False, verbose=Globals.VERB_NO):
    """ Runs network simulation based on the network model 'M' """

    print(" [+] Initialising the simulation...")
    print(" [+] Total simulation time is {:.2f} time units".format(t))

    # initialise simpy environment
    env = simpy.Environment()

    # bind the network model 'M' to the SimPy simulation environment
    network = Simulator.setup_network(env, M, verbose=verbose)
    print(" [+] Simulations started...")

    # show progress bar
    if bar:
        print("\n [ Running progress bar ]")
        progress_bar = ProgressBar.setup(env, t)
        progress_bar.run()

    # run the simulation
    env.run(until=t)

    if bar:
        print("\n")

    print(" [+] Simulation completed")

    # print summary statistics
    TraceUtils.print_stats(network, verbose=verbose)

    # if 'output_dir' is defined, save node names, queue monitor, and traces
    if output_dir is not None:
        TraceUtils.save_node_names(network, output_dir)
        TraceUtils.save_queue_mon(output_dir, network)

        # save generated, forwarded, received, discarded packets
        for trace in ['g', 'f', 'r', 'd']:
            TraceUtils.save_node_pkts(network, output_dir, trace)
