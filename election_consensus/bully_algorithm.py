import time
from constants import ELECTION_WAIT
from components.message import Message,print_msg
from components.network import Network

class BullyAlgorithm:
    def __init__(
        self,
        network:Network
        ) -> None:
        """Constructor for the consensus algorithm

        Args:
            network (Network): The network of the peer
        """
        self.network = network
        self.election_ongoing = False
        self.wait_time = ELECTION_WAIT
        self.last_updated = None
        self.last_win_updated = int(time.time())
        self.winning_candidate = None
        
    def start_election(self):
        """Used to start an election
        """
        
        # if election is already ongoing do nothing
        if self.election_ongoing:
            return
        print_msg("Election Started")
        
        # update the election parameters
        self.update_election(self.network.get_id())
        
        # generate campaign message and broadcast ir
        election_msg = self.generate_campaign_message()
        self.network.broadcast(election_msg)
        
    def check_win(self):
        """This function is called whenever there is change in state
        """
        if self.election_ongoing:
            print_msg("Checking winner")
            print_msg(int(time.time())-self.last_updated)
            
        if self.election_ongoing and self.last_updated_before_threshold():
            # if you sent an election message and its past timeout send leader message
            if self.winning_candidate == self.network.get_id():
                self.send_success()
                
            # if you are not leader wait for timeout to restart election
            elif self.timeout_for_win():
                print_msg("Timeout waiting for win message")
                self.end_election()
                self.start_election()
    
    def process_election_msg(self,msg:Message):
        """Function used to deal with recieving an election message

        Args:
            msg (Message): The recieved message
        """
        
        # if its a win message then end the election and update your leader
        if msg.is_win():
            print_msg(f"Recieved win message from {msg.sender_id}")
            self.end_election()
            self.network.update_leader(msg)
        
        # in case of an election message
        elif msg.is_campaign():
            
            # if you updated leader before threshold then ignore
            if not self.updated_win_before_threshold():
                print_msg("Discarding because win updated before threshold")
                
            # if sender id is greater then your id discard its message 
            # and participate in election by campaigning if didn't
            elif msg.sender_id > self.network.get_id():
                print_msg(f"Discareded leader request from {msg.sender_id}")
                if not self.election_ongoing:
                    print_msg("Sending campaign message")
                    self.start_election()
            
            # else update the candidate
            else:
                print_msg("Updated candidate")
                self.update_election(msg.sender_id)
        
    def update_election(self,_id:int):
        """Used to update the election state

        Args:
            _id (int): The id of the new best candidate
        """
        self.election_ongoing = True
        self.winning_candidate = _id
        self.last_updated = int(time.time())
        
    def end_election(self):
        """Function used to denote end of the election
        """
        self.last_win_updated = int(time.time())
        self.election_ongoing = False
        self.last_updated = None
        self.winning_candidate = None
    
    def updated_win_before_threshold(self) -> bool:
        """Check if winner was updated before threshold

        Returns:
            bool: True if it was
        """
        curr_time = int(time.time())
        return curr_time - self.last_win_updated > self.wait_time
    
    def last_updated_before_threshold(self) -> bool:
        """Chech if the last message recieved was before threshold

        Returns:
            bool: True if it was
        """
        if self.last_updated is None:
            return False
        curr_time = int(time.time())
        return curr_time - self.last_updated > self.wait_time
    
    def timeout_for_win(self) -> bool:
        """Check if there has been a timeout in recieving the win message

        Returns:
            bool: Yes if it has
        """
        if self.last_updated is None:
            return False
        curr_time = int(time.time())
        return curr_time - self.last_updated > self.wait_time*1.5
        
    def send_success(self):
        """Send a winner message for the election
        """
        self.end_election()
        win_msg = self.generate_win_message()
        self.network.broadcast(win_msg)
        self.network.update_leader(win_msg)
        self.end_election()
    
    def generate_campaign_message(self) -> Message:
        """Generate a campaign message

        Returns:
            Message: The message to send
        """
        return Message(
            msg_type="CAMPAIGN",
            sender_id=self.network.get_id(),
            reciever_id="all",
            msg="I want to be leader"
        )
    
    def generate_win_message(self) -> Message:
        """Send a winner message

        Returns:
            Message: The message to send
        """
        return Message(
            msg_type="WIN",
            sender_id=self.network.get_id(),
            leader_port=self.network.get_port(),
            reciever_id="all",
            msg="I am leader now"
        )