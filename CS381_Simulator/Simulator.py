""" Simulator.py """

import simpy

from . import Components
from . import Globals


def setup_network(env, M, verbose=Globals.VERB_NO):
    """ Bind the model graph 'M' to the SimPy simulation environment 'env' """

    print(" [+] Found {:d} nodes and {:d} links".format(len(M.G.nodes()), len(M.G.edges())))

    # create simulation network model
    network = create_network_model(env, M, verbose)

    # activate node interfaces (this sets SimPy processes)
    for node_name in network:
        network[node_name].if_up()

##        if node_name not in ['13', '14']:
##            network[node_name].if_up()           # double check it
            
##        if node_name == '13':
##            network[node_name].if_up()
##
##        if node_name == '14':
##            network[node_name].if_up()
          
    return network


def create_network_model(env, M, verbose=Globals.VERB_NO):
    """ Creates network: creates network nodes, binds connections to the nodes """

    network = {}

    # create nodes
    for node_name in M.G.nodes():

        network[node_name] = Components.Node(env, M, node_name, verbose)

    # create node links
    conn_dict = init_conn(env, M)

    # bind connections to the nodes
    for c in conn_dict:

        node_name1 = c[0]
        node_name2 = c[1]

        # Note: conn_a and conn_b are the same connection pipe viewed
        # from a-b and b-a perspectives
        conn_1 = conn_dict[c][0]
        conn_2 = conn_dict[c][1]

        # bind interfaces to nodes
        network[node_name1].add_conn(node_name2, conn_1)
        network[node_name2].add_conn(node_name1, conn_2)

    return network


def init_conn(env, M):
    """
    Creates connection pipes.

    Keys of 'conn_dict' are tuples that contain the two node names,
    and values are tuples that contain the two connection objects,
    belongings to each node.
    """

    # initialise connections dictionary
    conn_dict = {}

    # loop over all edges in the network graph
    for c in M.G.edges():

        # fetch the link attributes for this edge
        link_attr_dict = M.G[c[0]][c[1]]
        # fetch the capacity and transmission delay for this link
        link_capacity = link_attr_dict[Globals.LINK_CAPACITY_KWD]
        transm_delay = link_attr_dict[Globals.LINK_TRANSM_DELAY_KWD]

        # create two communication pipes, 1->2 and 2->1
        pipe_12 = simpy.Store(env, capacity=link_capacity)
        pipe_21 = simpy.Store(env, capacity=link_capacity)

        # create two connection objects
        conn_1 = Components.Channel(env, transm_delay, pipe_12, pipe_21)
        conn_2 = Components.Channel(env, transm_delay, pipe_21, pipe_12)

        # add the connection to the dictionary
        conn_dict[c] = (conn_1, conn_2)

    return conn_dict
