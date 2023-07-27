from .network import Network
from .server import Server
from .inputs import Input
from .message import Message,print_msg
from .connection import Connection
from election_consensus.bully_algorithm import BullyAlgorithm
from constants import HOST

from typing import Union
import socket
import select
import sys

class Node:
    def __init__(
        self,
        server_port:int,
        is_genesis:bool=False,
        leader_port:int=None,
        ) -> None:
        """Constructor for the Peer

        Args:
            server_port (int): The port of the server for the current network
            is_genesis (bool, optional): If the current node is genesis. Defaults to False.
            leader_port (int, optional): The port of the leader if it is not genesis. Defaults to None.
        """
        self.network = Network(
            server_port=server_port,
            is_genesis=is_genesis,
            leader_port=leader_port
        )
        
        self.election_manager = BullyAlgorithm(
            network=self.network
        )
        
        self.server = Server(
            port=server_port,
            network=self.network,
            election_manager=self.election_manager
        )
        
        self.input = Input(
            network=self.network
        )
        
        # add the server and std input as the fd to listen to
        self.network.inputs.extend([self.input,self.server])
        
        # if it is not genesis then connect to all the node of previous cluster
        if not is_genesis:
            self.create_connections_with_existing_nodes()
            
    def event_loop(self):
        """Starts an event loop
        """
        try:
            perform_print = True
            # while the network is running
            while self.network.running:
                # print a token to dicplay ready for input
                if perform_print:
                    print("\n>>",end=" ")
                    perform_print = False
                sys.stdout.flush()
                
                # find out all the fds that are changed with timeout of 1
                # TODO set a better timeout
                readable_items, writable_items, exceptional = select.select(self.network.inputs, self.network.outputs, [],1)
                
                # for all the readables call their on read method
                for readable in readable_items:
                    readable.on_read()
                    perform_print = True
                    
                # for all the writable call the on write method
                for writable in writable_items:
                    writable.on_write()
                    # remove this from the list of writable
                    self.network.remove_request(writable)
                    perform_print = True
                    
                # at each iteration let the elction manager run it timer
                self.election_manager.check_win()
        except KeyboardInterrupt:
            self.network.terminate()
    
    def create_connections_with_existing_nodes(self):
        """Used to create connection with the existing node of the cluster
        """
        
        # get the network after connecting with the leader
        network = self.connect_with_genesis_and_get_all_existing_node()
        
        for node_id,port in network.items():
            node_id = int(node_id)
            if node_id in self.network.network_servers:
                continue
            
            # create a new connection with a peer
            client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client_socket.connect((HOST,port))
            
            # send a ping message
            ping_message = self.generate_ping_message(
                sender_id=self.network.get_id(),
                reciever_id=node_id
            )
            ping_message.display_sent()
            client_socket.send(ping_message.get_msg_buff())
            
            # add it to list of connections
            self.add_verified_connection(
                conn=client_socket,
                conn_id=node_id,
                port=port
            )
        
    def connect_with_genesis_and_get_all_existing_node(self) -> dict:
        """Used to connect with the leader and get all the existing peers

        Returns:
            dict: A dictionary of server of the peer ids
        """
        # create a new connection with leader port
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_socket.connect((HOST,self.network.get_leader_port()))
        
        # send a ping message for verification
        ping_message = self.generate_ping_message("New Node","leader")
        ping_message.display_sent()
        client_socket.send(ping_message.get_msg_buff())
        
        # recieve a pong message and use it to update network
        pong_message = Message(bts=client_socket.recv(2048))
        pong_message.display()
        
        # update the values and add it to list of connections
        network = self.network.update_with_pong(pong_message)
        self.add_verified_connection(
            conn = client_socket,
            conn_id = self.network.get_leader_id(),
            port = self.network.get_leader_port()
        )
        return network
    
    def add_verified_connection(
        self,
        conn:socket.socket,
        conn_id:int,
        port:int
        ):
        """Used to add a connection to the list of verified ones

        Args:
            conn (socket.socket): The socket to add
            conn_id (int): The id of the connection
            port (int): The port to connect to
        """
        
        # create a new connection object and verify ot
        new_connection = Connection(
            conn=conn,
            conn_id = conn_id,
            network=self.network,
            election_manager=self.election_manager
        )
        new_connection.verify()
        
        # Add it to the network
        self.network.append_connection(new_connection,conn_id)
        self.network.add_new_server_with_id(conn_id,port)
        
    def generate_ping_message(self,sender_id:Union[int,str],reciever_id:Union[int,str]) -> Message:
        """Generates a ping message

        Args:
            sender_id (int|str): id of the sendor
            reciever_id (int|str): Id of the reciever

        Returns:
            Message: The message object
        """
        return Message(
                msg_type="PING",
                msg="want to connect",
                server_port = self.network.server_port,
                sender_id = sender_id,
                reciever_id = reciever_id
            )