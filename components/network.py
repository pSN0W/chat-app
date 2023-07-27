from .send_request import SendRequest
from typing import List,Dict,Optional
from .message import Message,print_msg

class Network:
    def __init__(
        self,
        server_port:int,
        is_genesis:bool = False,
        leader_port:int = None
        ) -> None:
        """Constructor for the network

        Args:
            server_port (int): The port of the server for the current network
            is_genesis (bool, optional): If the current node is genesis. Defaults to False.
            leader_port (int, optional): The port of the leader if it is not genesis. Defaults to None.
        """
        self.server_port = server_port
        
        # if the port is genesis then initialise everything
        if is_genesis:
            self.leader_port = server_port
            self.curr_network_size = 0
            self.id = 0
            self.leader_id = 0
        else:
            self.leader_port = leader_port
            
        self.running = True # the peer is running
        self.network_servers:Dict[int,int] = {} # Dict[peer_id,peer_port]
        self.id_to_connections = {} # id to connection object
        
        # all the fd whose input to check
        self.inputs:list = []
        
        # all the fds whose output to check
        self.outputs: List[SendRequest] = []
        
    def append_connection(self,conn,conn_id:int):
        """Used to add a connection to the network

        Args:
            conn (Connection): The connection object to add
            conn_id (int): The id of the connection
        """
        self.id_to_connections[conn_id] = conn
        self.inputs.append(conn)
        print_msg(f"New connection {conn_id} made")
        
    def add_send_request(self,con_id:int,msg:Message):
        """Used to add a send request to a peer

        Args:
            con_id (int): Id of the peer to send message to
            msg (Message): The message to send
        """
        # check if there is an id with this connection and if it is verified
        if con_id not in self.id_to_connections:
            print_msg("No connection with this id")
            return
        
        conn = self.id_to_connections[con_id]
        if not conn.is_verified():
            print_msg("Connection not verified")
            return
        
        # find the SendRequest with the peer you want to send message to
        req = self.find_send_request(conn)
        
        # if it exists then add one more message to its queue
        if req is not None:
            req.add_message(msg)
            
        # if it doesn't than create a new SendRequet and add it to outputs
        else:
            req = SendRequest(conn.get_conn(),conn.get_id())
            req.add_msg(msg)
            self.outputs.append(req)
            
    def add_new_server(self,port:int):
        """Used to add a new server to the networ

        Args:
            port (int): The port to add
        """
        self.add_new_server_with_id(self.get_connection_id(),port)
        
    def add_new_server_with_id(self,_id:int,port:int):
        """Adds a new server with the given id

        Args:
            _id (int): id of the peer
            port (int): port of the peer
        """
        self.network_servers[_id] = port
        
    def update_with_pong(self,msg:Message) -> dict:
        """Updates the network parameters after recieving the pong message

        Args:
            msg (Message): The message recieved in pong

        Returns:
            dict[peer_id,peer_port]: Rest of the networks in the cluster
        """
        if not msg.is_pong():
            return
        data = msg.get_msg()
        self.set_leader_id(int(data.get("leader_id")))
        self.set_id(int(data.get("reciever_id")))
        self.set_network_size(self.get_id())
        
        return data.get("network")
    
    def update_leader(self,msg:Message):
        """Used to update the leader of the cluster as the sender of the message

        Args:
            msg (Message): Message for updation
        """
        data = msg.get_msg()
        self.set_leader_id(data['sender_id'])
        self.set_leader_port(data['leader_port'])
        
    def find_send_request(self,conn) -> Optional[SendRequest]:
        """Find the request with the same fd as the connection

        Args:
            conn (Connection): The socket with shich we neet to find the same SendRequest

        Returns:
            Optional[SendRequest]: None if no send request found else the SendRequest
        """
        # match the socket of both of them to find the SendRequest
        for req in self.outputs:
            if conn.get_conn() == req.get_conn():
                return req
        return None
    
    def remove_request(self,req:SendRequest):
        """Remove a request from outputs if it doesn't have any messages in the queue

        Args:
            req (SendRequest): The SendRequest to chech
        """
        # if queue is empty then remove
        if req.empty():
            self.outputs.remove(req)
            
    def remove_connection(self,conn):
        """Closes a connection

        Args:
            conn (Connection): The connection to close
        """
        # remove it form the connection dictionary
        self.id_to_connections.pop(conn.get_id())
        
        # remove it from the list we are listening to
        self.inputs.remove(conn)
        
        # if it is in network server then remove it
        if conn.is_verified():
            self.network_servers.pop(conn.get_id())
        
        # find all the write request to this connection adn remove them
        req = self.find_send_request(conn)
        if req is not None:
            self.outputs.remove(req)
        
    def terminate(self):
        """Close the peer
        """
        
        # for each peer in the network close connection with them and remove them
        for peer_con in list(self.id_to_connections.values()).copy():
            peer_con.get_conn().close()
            self.remove_connection(peer_con)
        
        # set peer running to false
        self.running = False
        print("\nTerminated Safely",end="")
    
    def broadcast(self,msg:Message):
        """Send message to each peer in the network

        Args:
            msg (Message): The message to send
        """
        
        # add this message to each peer
        for peer_id in self.id_to_connections:
            self.add_send_request(peer_id,msg)
        
    def i_am_leader(self) -> bool:
        """If the current peer is the leader

        Returns:
            bool: True if it is
        """
        return self.id == self.leader_id
    
    def get_port(self)->int:
        """PORT of the current peer

        Returns:
            int: PORT
        """
        return self.server_port
    
    def get_leader_port(self)->int:
        """Get the port of the leader of the network

        Returns:
            int: PORT
        """
        return self.leader_port
    
    def get_leader_id(self) -> int:
        """Get the id of the leader

        Returns:
            int: leader id
        """ 
        return self.leader_id
    
    def get_connection_id(self) -> int:
        """Gets the connection id for the latest connection

        Returns:
            int: The id for the leates connction
        """
        # new id will be equal to the current network size
        return self.curr_network_size
    
    def get_new_connection_id(self) -> int:
        """Returns connection id for a new node that wants to join

        Returns:
            int: The id of the connection
        """
        self.curr_network_size += 1
        return self.curr_network_size
    
    def get_id(self) -> int:
        """Get current network id

        Returns:
            int: current peer id
        """
        return self.id
    
    def get_network_servers(self) -> Dict[int,int]:
        """Gets all the network in the cluster

        Returns:
            Dict[int,int]: Dictionary of peer_id and PORT
        """
        return self.network_servers.copy()
    
    def set_leader_port(self,port:int):
        """Set a new leader port

        Args:
            port (int): New port for leader
        """
        self.leader_port = port
    
    def set_id(self,_id:int):
        """Used to set id for the peer

        Args:
            _id (int): Id of the peer
        """
        self.id = _id
        
    def set_leader_id(self,leader_id:int):
        """Used to set id for the leader

        Args:
            leader_id (int): new leader id
        """
        self.leader_id = leader_id
        
    def set_network_size(self,network_size:int):
        """Used to set the size of the network

        Args:
            network_size (int): Set size of the network
        """
        self.curr_network_size = network_size