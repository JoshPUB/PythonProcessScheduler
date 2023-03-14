""" Globals.py """

# Version
VERSION = 0
REVISION = 3
SUBREV = 3

# Queue monitoring interval
QUEUE_MONITOR_DELTAT = 0.001

# Network model keywords- model graph definition keywords
MODEL_NAME_KWD = 'model_name'

# Node attribute keywords
NODE_TYPE_KWD = 'type'
NODE_PKT_RATE_KWD = 'node_pkt_rate'

# Packet processing delay
NODE_PROC_DELAY_KWD = 'node_proc_delay'

# Node queue cutoff
NODE_QUEUE_CUTOFF_KWD = 'node_queue_cutoff'

# The interval for checking the queue when not locked in processing
NODE_QUEUE_CHECK_KWD = 'node_queue_check'

# Link attribute keywords
LINK_CAPACITY_KWD = 'link_capacity'  # link capacity

# Delay in packet transmission through the link
LINK_TRANSM_DELAY_KWD = 'link_transm_delay'

# The table of shortest paths
PATH_G_KWD = 'path_G'


# Packet structure keywords
TIME_STAMP = 'time_stamp'
ID = 'id'
SOURCE = 'source'
DEST_NODE = 'dest_node'
# CURRENT_STATUS = 'current_status'
# PRIORITY_LEVEL = 'priority_level'
HOP_NODE = 'hop_node'
NO_HOPS = 'no_hops'
NO_ROUNDS = 'no_rounds'
DEST_TIME_STAMP = 'dest_time_stamp'
PRIORITY = 'priority'
CPU_BURST = 'cpu_burst'
CPU_BURST_COPY = 'cpu_burst_copy'
SIZE = 'size'
SIZE_COPY = 'size_copy'
SERVICE_TIME = 'service_time'
NONE = 'none'

# Suffixes for input files
TOPO_SUFFIX = ".topo"
TYPE_SUFFIX = ".type"
PARAM_SUFFIX = ".param"

# Suffix for pickling the model
PICKLE_SUFFIX = ".pickle"

# Suffixes for output files
NODES_LIST_FILE = 'nodes.dat'
GEN_SUFFIX = '_gen.csv'
FWD_SUFFIX = '_fwd.csv'
DISCARD_SUFFIX = '_discard.csv'
RECV_SUFFIX = '_recv.csv'
QUEUE_SUFFIX = '_queue.csv'

# Define verbose levels
VERB_NO = 0
VERB_LO = 1
VERB_HI = 2
VERB_EX = 3

# Simulation progress bar
BAR_LENGTH = 40

TYPE = "type"