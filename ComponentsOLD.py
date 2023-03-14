""" Components.py """

import random
import numpy as np
import collections                              # provides 'deque': double-ended queue
import inspect
import math
import networkx as nx

from CS381_Simulator import Globals
from CS381_Simulator import Utils
from CS381_Simulator import PacketGenerator

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
            if len(self.proc_queue) > 0:
                # get the first packet from the queue
                pkt = self.proc_queue.popleft()

                # get the source node
                source_node = pkt[Globals.SOURCE]

                # get the destination node
                dest_node = pkt[Globals.DEST_NODE]

                # report as per verbose level
                if self.verbose >= Globals.VERB_LO:
                    Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name + '_get', self.verbose)

                # if the destination is this current node
                if dest_node == self.name:
                    
                    # incur packet processing time
                    yield self.env.timeout(random.expovariate(self.proc_delay))

                    # set the destination arrival time
                    pkt[Globals.DEST_TIME_STAMP] = self.env.now

                    # packet terminates here- put it in the receive queue
                    self.received.append([self.env.now, pkt])

                    # report as per verbose level
                    if self.verbose >= Globals.VERB_LO:
                        Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name + '_sink', self.verbose)


                # if the destination is some other node, forward this packet then
                else:

                    # incur packet processing time
                    yield self.env.timeout(random.expovariate(self.proc_delay))
                    
                    # increment the packet hop counter
                    pkt[Globals.NO_HOPS] += 1

                    # get next-hop node along the shortest path
                    hop_node = self.path_G[(self.name, dest_node)]

                    # register the next-hop node with the packet
                    pkt[Globals.HOP_NODE] = hop_node

                    # forward packet to the next-hop node
                    self.send_to_node(pkt, hop_node)

                    # count this packet as sent to 'hop_node'
                    self.pkt_sent[hop_node] += 1

                    #register forwareded packets in the forwards queue, maybe self.proc_queue.append(pkt)
                    self.forwarded.append([self.env.now, pkt])

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
        if int(self.name) in [1, 2, 3, 4, 5, 6, 7, 8]:
            
            while True:

                # Find the arrival time of the next packet/process
                deltat = PacketGenerator.run(self.pkt_rate)

                # incur packet arrival time
                yield self.env.timeout(deltat)

                # get the destination node
                dest_node = str(random.choice([13, 14, 15, 16]))

                # get the type
                type = " "

                if dest_node == "13":
                    type = "Mail"

                if dest_node == "14":
                    type = "Media"

                if dest_node == "15":
                    type = "Storage"

                if dest_node == "16":
                    type = "Navigation"

                # generate the packet
                pkt = self.make_pkt(dest_node, type)

                # add the packet to the end of the queue of the source node queue
                self.proc_queue.appendleft(pkt)
                
                # report the generated packet in the source node
                self.generated.append([self.env.now, pkt])

                # report as per verbose level
                if self.verbose >= Globals.VERB_LO:
                    Utils.report(self.env.now, self.name, pkt, self.proc_queue, inspect.currentframe().f_code.co_name, self.verbose)


    def make_pkt(self, dest_node, type):
        """ Creates a network packet """

        pkt = {
               Globals.TIME_STAMP: self.env.now,
               Globals.ID: Utils.gen_id(),
               Globals.SOURCE: self.name,
               Globals.DEST_NODE: dest_node,
               Globals.HOP_NODE: Globals.NONE,
               Globals.DEST_TIME_STAMP: -1.0,
               Globals.NO_HOPS: 0,
               Globals.TYPE: type
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
