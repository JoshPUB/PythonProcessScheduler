""" TraceUtils.py """

import os

from . import Globals
from . import IO
from . import Utils


def print_stats(network, verbose=Globals.VERB_NO):
    """ Print statistics collected during the simulation run """

    print(" [+] Printing summary statistics:")

    grand_tot_sent = 0
    grand_tot_recv = 0

    for n in network:

        node = network[n]

        if verbose > Globals.VERB_NO:
            print("\n Node {:s} [{:s}]:".format(n, node.type))

        tot_pkt_sent = 0
        tot_pkt_recv = 0

        if verbose > Globals.VERB_NO:
            print("\t Total packets generated: {:,}"
                  .format(len(node.generated)))
            print("\t Total packets forwarded: {:,}"
                  .format(len(node.forwarded)))

        for c in node.conns:

            if verbose > Globals.VERB_NO:
                print("\t -> connection to {:s}".format(c))
                print("\t    sent {:,}".format(node.pkt_sent[c]))
                print("\t    recv {:,}".format(node.pkt_recv[c]))

            tot_pkt_sent = tot_pkt_sent + node.pkt_sent[c]
            tot_pkt_recv = tot_pkt_recv + node.pkt_recv[c]

        if verbose > Globals.VERB_NO:
            print("\t [ total sent: {:,} ]".format(tot_pkt_sent))
            print("\t [ total recv: {:,} ]".format(tot_pkt_recv))

        grand_tot_sent = grand_tot_sent + tot_pkt_sent
        grand_tot_recv = grand_tot_recv + tot_pkt_recv

    print("\n\tTotal packets sent: {:,}".format(grand_tot_sent))
    print("\tTotal packets recv: {:,}\n".format(grand_tot_recv))
    print("\tThroughput: {:,}\n".format(grand_tot_recv / grand_tot_sent))


def save_node_names(network, output_dir):
    """ Save the list of node names """

    file_name = Globals.NODES_LIST_FILE
    file_path = os.path.join(output_dir, file_name)

    fp = IO.open_for_writing(file_path)

    node_names = list(network.keys())
    node_names.sort()

    for node_name in node_names:
        fp.write("{:s}\n".format(node_name))

    IO.close_for_writing(fp)


def save_queue_mon(output_dir, network):
    """ For each node, saves node queue length as a function of simulation time """

    print(" [+] Saving queue monitors..")

    node_names = list(network.keys())
    node_names.sort()

    for node_name in node_names:

        node = network[node_name]
        node_name = node.name

        file_name = node_name + Globals.QUEUE_SUFFIX
        output_file = os.path.join(output_dir, file_name)

        fp = IO.open_for_writing(output_file)

        # each element of node.queue_mon is a list [time_now, queue_length]
        fp.write("stime,queue_length\n")
        for item in node.queue_mon:
            fp.write("{:f},{:d}\n".format(item[0], item[1]))

        IO.close_for_writing(fp)


def save_node_pkts(network, output_dir, queue_type):
    """ For given queue type: for all nodes saves all packets to a file """

    if queue_type == 'g':
        print(" [+] Saving generated packets..")
        suffix = Globals.GEN_SUFFIX
    elif queue_type == 'f':
        print(" [+] Saving forwarded packets..")
        suffix = Globals.FWD_SUFFIX
    elif queue_type == 'd':
        print(" [+] Saving discarded packets..")
        suffix = Globals.DISCARD_SUFFIX
    elif queue_type == 'r':
        print(" [+] Saving received packets..")
        suffix = Globals.RECV_SUFFIX
    else:
        Utils.error("Unknown queue '{:s}'".format(queue_type))

    node_names = list(network.keys())
    node_names.sort()

    for node_name in node_names:

        node = network[node_name]

        if queue_type == 'g':
            queue = node.generated
        elif queue_type == 'f':
            queue = node.forwarded
        elif queue_type == 'd':
            queue = node.discarded
        elif queue_type == 'r':
            queue = node.received
        else:
            Utils.error("Unknown queue 2 '{:s}'".format(queue_type))

        file_name = node.name + suffix
        node_file = os.path.join(output_dir, file_name)

        fp = IO.open_for_writing(node_file)
        fp.write("stime,timestamp,id,source,dest,nhops\n")

        for item in queue:
            stime, pkt = item
            fp.write("{:f},{:f},{:s},{:s},{:s},{:d}\n"
                     .format(stime, pkt[Globals.TIME_STAMP], pkt[Globals.ID],
                             pkt[Globals.SOURCE], pkt[Globals.DEST_NODE],
                             pkt[Globals.NO_HOPS]))

        IO.close_for_writing(fp)
