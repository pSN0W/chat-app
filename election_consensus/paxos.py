from components.message import Message
from components.network import Network
import random as rnd
from .tcp_connection import TCPConnectionElection
from components.network import Network

class Paxos(TCPConnectionElection):
    """Implementation of paxos leader election"""
    def __init__(self, network: Network) -> None:
        """Constructor for the consensus algorithm

        Args:
            network (Network): The network of the peer
        """
        super().__init__(network)
        self.network = Network
        self.curr_proposal_number = rnd.randint(1,1000)
        
        self.recieved_accept = set()
        
    def start_election(self):
        self.network.broadcast(
            Message(
                msg_type="CAMPAIGN",
                msg="I am contesting",
                sender_id=self.network.get_id(),
                reciever_id="all",
                proposal_number=self.curr_proposal_number,
                campaign_type="PROPOSE"
            )
        )
        
    def check_win(self):
        if len(self.recieved_accept)==len(self.network.get_network_servers()):
            self.network.broadcast(self.generate_win_message())
            
    def process_election_msg(self,msg:Message):
        
        if msg.is_win():
            self.network.update_leader(msg)
        data = msg.get_msg()
        
        # if proposal number is smaller then self then ignore other wise send accept
        if data["campaign_type"]=="PROPOSE":
            self.network.add_send_request(
                con_id=msg.sender_id,
                msg=Message(
                    msg_type="CAMPAIGN",
                    msg="I accept",
                    sender_id=self.network.get_id(),
                    reciever_id=msg.sender_id,
                    campaign_type="ACCEPT"
                )
            )
            
        # if campaign type is accept the add it to the list of nodes that have accepted
        elif data["campaign_type"] == "ACCEPT":
            self.recieved_accept.add(msg.sender_id)