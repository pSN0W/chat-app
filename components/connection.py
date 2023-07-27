from .message import Message, print_msg
from .network import Network
from election_consensus.bully_algorithm import BullyAlgorithm
import socket
from typing import Optional

class Connection:
    def __init__(
        self,
        conn:socket.socket,
        conn_id:int,
        network:Network,
        election_manager: BullyAlgorithm
        ) -> None:
        """A wrapper on socket connection class

        Args:
            conn (socket.socket): A sacket which will be used for communication
            conn_id (int): Connection id of communication
            network (Network): The constants defining the network
            election_manager (BullyAlgorithm): Algorithm used for leader election
        """
        conn.setblocking(False)
        self.connection = conn
        self.id = conn_id
        self.verified = False
        self.network = network
        self.election_manager = election_manager
        
    def on_read(self):
        """A function that will be called when the socket is free to read
        """
        # Recieve message
        msg = self.connection.recv(1024)
        
        # If there is a message then process accordingly
        if msg:
            
            # create an instance of Message
            msg = Message(bts=msg)
            
            # if the connection is not verified and is is sending messages discard
            if not msg.is_ping() and not self.is_verified():
                print_msg("Message without connection")
                
            # if an unverified connection is sending ping messages verify it
            # and ad its server to network
            elif msg.is_ping():
                self.verify()
                
                # if you are leader then send pong
                if self.network.i_am_leader():
                    self.send_pong()
                
                self.network.add_new_server(msg.get_msg()['server_port'])
            
            # if its an election message let the consnsus algo deal with it
            elif msg.is_election():
                self.election_manager.process_election_msg(msg)
                
            # else display the message
            else:
                msg.display()
        
        # Empty message shows that one of the peer have disconnected so you need to remove it
        else:
            # If the one to be disconnected is leader than start election
            if self.get_id() == self.network.get_leader_id():
                self.election_manager.start_election()
            self.network.remove_connection(self)
    
    def send_pong(self):
        """Generate pong message to send it contains the information about the network
        """
        pong_msg = Message(
            sender_id = self.get_id(),
            reciever_id = self.network.get_connection_id(),
            msg_type = "PONG",
            leader_id = self.network.get_leader_id(),
            network = self.network.get_network_servers(),
            msg="Connection Accepted"
        )
        self.network.add_send_request(self.get_id(),pong_msg)
    
    def verify(self):
        """Verify a connection
        """
        self.verified = True
    
    def fileno(self)->int:
        """Used by select to know which file descriptor is being used

        Returns:
            int: file descriptor
        """
        return self.connection.fileno()
        
    def is_verified(self) -> bool:
        """If the connection is verified

        Returns:
            bool: is connection verified
        """
        return self.verified
        
    def get_id(self) -> int:
        """Get the id of the connection

        Returns:
            int: id
        """
        return self.id
    
    def get_conn(self) -> socket.socket:
        """Socket of the connection

        Returns:
            socket.socket: connection
        """
        return self.connection
        