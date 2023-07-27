from components.message import Message
from .bully_algorithm import BullyAlgorithm
from v6.components.network import Network

class TCPConnectionElection(BullyAlgorithm):
    """Since the communication channel is trustworthy we can check which of the nodes are alive. Within all the alive nodes the one with the lowest id is chosen
    """
    def __init__(self, network: Network) -> None:
        super().__init__(network)
        self.network = network
        
    def start_election(self):
        """Start the election"""
        if min(self.network.network_servers.keys()) == self.network.get_id():
            msg = self.generate_win_message()
            self.network.broadcast(msg)
            
    def check_win(self):
        """No action required for this case"""
        pass
    