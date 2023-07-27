from v6.components.network import Network
from .tcp_connection import TCPConnectionElection
from components.network import Network
from components.message import Message

class Raft(TCPConnectionElection):
    """Raft leader election algorithm"""
    def __init__(self, network: Network) -> None:
        super().__init__(network)
        self.network = network
        self.my_state = "FOLLOWER"
        
    def check_win(self):
        if self.timeout_for_win():
            poss_connection = self.network.id_to_connections[min(self.network.network_servers.keys())]
            self.network.remove_connection(poss_connection)
            self.start_election()