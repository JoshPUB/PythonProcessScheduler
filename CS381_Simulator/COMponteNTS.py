""" Components.py """

import random
import numpy as np
import collections                              # provides 'deque': double-ended queue
import inspect
import math
import networkx as nx

from . import Globals
from . import Utils
from . import PacketGenerator

class Channel:
    """ Model a connection between two nodes """

    def __init__(self, env, delay, conn_out, conn_in):
        self.env = env
        self.delay = delay
        self.conn_out = conn_out
        self.conn_in = conn_in

    def latency(self, pkt):
        """ Latency for putting packet onto the wire """
        yield self.env.timeout(self.delay)

        self.conn_out.put(pkt)

    def put(self, pkt):
        """ Puts the packet 'pkt' onto the wire """
        self.env.process(self.latency(pkt))

    def get(self):
        """ Retrieves packet from the connection """
        return self.conn_in.get()


class Node:
    """ Model a network node """

    def __init__(self, env, M, node_name, verbose):

        self.env = env          # SimPy environment
        self.name = node_name   # must be unique
        self.type = M.G.nodes[node_name][Globals.NODE_TYPE_KWD]
        self.pkt_rate = M.G.nodes[node_name][Globals.NODE_PKT_RATE_KWD]
        self.proc_delay = M.G.nodes[node_name][Globals.NODE_PROC_DELAY_KWD]
        self.queue_check = M.G.nodes[node_name][Globals.NODE_QUEUE_CHECK_KWD]
        self.queue_cutoff = M.G.nodes[node_name][Globals.NODE_QUEUE_CUTOFF_KWD]

        # precomputed table of shortest paths
        self.path_G = M.shortest_paths
        self.nodes = nx.nodes(M.G)

        self.conns = {}
        self.verbose = verbose

        # processing queue and queue length monitor
        self.proc_queue = collections.deque()
        self.queue_mon = collections.deque()

        # packets persistent storage
        self.generated = collections.deque()
        self.received = collections.deque()
        self.forwarded = collections.deque()
        self.discarded = collections.deque()

        # counters for sent/received packets (key=node name)
        self.pkt_sent = {}
        self.pkt_recv = {}

        # dt interval for incoming queue monitoring
        self.queue_monitor_deltat = Globals.QUEUE_MONITOR_DELTAT
        

    def add_conn(self, c, conn):
        """ Add a connection from this node to the node 'c' """

        self.conns[c] = conn
        self.pkt_sent[c] = 0
        self.pkt_recv[c] = 0
        

    def if_up(self):
        """ Activates interfaces- this sets up SimPy processes """

        # start receiving processes on all receiving connections
        for c in self.conns:
            self.env.process(self.if_recv(c))

        # activate packet generator, packet forwarding, queue monitoring
        self.env.process(self.pkt_gen_process())
        self.env.process(self.forward_process())
        self.env.process(self.queue_monitor())
        

    def if_recv(self, c):
        """ Node receive interface from node 'c' """

        # the connection from 'self.name' to 'c'
        conn = self.conns[c]

        while True:

            # pick up any incoming packets
            pkt = yield conn.get()

            # increment the counter for this sending node
            self.pkt_recv[c] += 1

            # put the packet in the processing queue
            self.proc_queue.append(pkt)

            # report as per verbose level
            if self.verbose >= Globals.VERB_LO:
                Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name, self.verbose)
                

    def forward_process(self):
        """ Node packet forwarding process """

        while True:

            # if there are any packets in the processing queue

                # get the first packet from the queue
                

                # get the source node
                

                # get the destination node
                

                # report as per verbose level
                if self.verbose >= Globals.VERB_LO:
                    Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name + '_get', self.verbose)

                # if the destination is this current node
                
                    
                    # incur packet processing time
                    

                    # set the destination arrival time


                    # packet terminates here- put it in the receive queue
                    

                    # report as per verbose level
                    if self.verbose >= Globals.VERB_LO:
                        Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name + '_sink', self.verbose)


                # if the destination is some other node, forward this packet then
                else:

                    # incur packet processing time

                    
                    # increment the packet hop counter
                    

                    # get next-hop node along the shortest path
                    

                    # register the next-hop node with the packet
                    

                    # forward packet to the next-hop node
                    

                    # count this packet as sent to 'hop_node'


                    # report as per verbose level
                    if self.verbose >= Globals.VERB_LO:
                        Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name + '_fwd', self.verbose)


            # if there are no packets in the processing queue
            else:

                # incur queue check delay
                yield self.env.timeout(self.queue_check)
                

    def send_to_node(self, pkt, next_node):
        """ Sends packet to the destination node """

        # get the connection to the destination node
        conn = self.conns[next_node]
        conn.put(pkt)  # put the packet onto the connection

        # report as per verbose level
        if self.verbose > Globals.VERB_NO:
            Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name, self.verbose)
            

    def pkt_gen_process(self):
        """ Process that generates networks packets """

        # Determine what nodes can generate packets/processes

            
            while True:

                # Find the arrival time of the next packet/process 
                

                # incur packet arrival time
                

                # get the source node


                # get the destination node


                # generate the packet
                

                # add the packet to the end of the queue of the source node queue  
                
                
                # report the generated packet in the source node
                

                # report as per verbose level
                if self.verbose >= Globals.VERB_LO:
                        Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name, self.verbose)


    def make_pkt(self, dest_node):
        """ Creates a network packet """

        pkt = {
               Globals.TIME_STAMP: self.env.now,
               Globals.ID: Utils.gen_id(),
               Globals.SOURCE: self.name,
               Globals.DEST_NODE: dest_node,
               Globals.HOP_NODE: Globals.NONE,
               Globals.DEST_TIME_STAMP: -1.0,
               Globals.NO_HOPS: 0
               }

        return pkt
    

    def discard_packet(self, pkt, msg):
        """ Discards the packet (puts the packet into the node packet sink) """

        # place this packet in the node sink
        self.discarded.append([self.env.now, pkt])


    def queue_monitor(self):
        """ Queue monitor process """

        while True:
            # add to queue monitor time now and queue_length
            self.queue_mon.append([self.env.now, len(self.proc_queue)])

            # incur monitor queue delay  [queue_check = 0.001]
            yield self.env.timeout(self.queue_monitor_deltat)
