from components.node import Node
import sys

node = None

# get the command line arguments
leader_port = int(sys.argv[1])
host_port = int(sys.argv[2]) if len(sys.argv)>2 else None

# generate a node using those arguments
if host_port is None:
    node = Node(server_port=leader_port,is_genesis=True)
else:
    node = Node(server_port=host_port,leader_port=leader_port)
    
# start event loop for that node
node.event_loop()
