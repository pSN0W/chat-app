import socket
from constants import HOST
from .connection import Connection
from .network import Network
from election_consensus.bully_algorithm import BullyAlgorithm

class Server:
    
    def __init__(
        self,
        port:int,
        network: Network,
        election_manager: BullyAlgorithm) -> None:
        """Creates a server for the current peer

        Args:
            port (int): The port of the server
            network (Network): network of the peer
            election_manager (BullyAlgorithm): The leader election consensus used
        """
        self.network = network
        self.election_manager = election_manager
        
        # create a new socket for the peer
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.bind((HOST,port))
        self.connection.listen(10)
        self.connection.setblocking(False)
        
    def fileno(self) -> int:
        """Used by select to know which file descriptor is being used

        Returns:
            int: file descriptor
        """
        return self.connection.fileno()
    
    def on_read(self):
        """A function that will be called when there is anything to read
        """
        
        # if the server is accepting then there is a new connection waiting
        # accept that connection
        conn,_ = self.connection.accept()
        
        # create a new connection id for that connection
        conn_id = self.network.get_new_connection_id()
        new_connection = Connection(
            conn=conn,
            conn_id=conn_id,
            network=self.network,
            election_manager=self.election_manager
        )
        
        # add it to the list of connections to listen to
        self.network.append_connection(new_connection,conn_id)