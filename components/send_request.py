import queue
from .message import print_msg,Message
import socket

class SendRequest:
    def __init__(
        self,
        conn:socket.socket,
        con_id:int) -> None:
        """Constructor for the send request

        Args:
            conn (socket.socket): The socket to send message to
            con_id (int): The id of the socket
        """
        self.connection = conn
        self.id = con_id
        self.msg_queue = queue.Queue()
        
    def add_msg(self,msg:Message):
        """Adds a message to its queue

        Args:
            msg (Message): The message to add
        """
        self.msg_queue.put(msg)
        
    def on_write(self):
        """Function to call on write
        """
        
        # if empty then do nothing
        if self.empty():
            print_msg("Message queue is empty")
            
        # get the latest message from the queue and encode and send it
        else:
            msg = self.get()
            msg.display_sent()
            self.connection.send(msg.get_msg_buff())
            
    def fileno(self) -> int:
        """Used by select to identify the opened fd

        Returns:
            int: The fd of the connection
        """
        return self.connection.fileno()
    
    def get(self)->Message:
        """Gets the latest message

        Returns:
            Message: Latest message
        """
        return self.msg_queue.get()
    
    def get_conn(self) -> socket.socket:
        """Returns the socket of the connection

        Returns:
            socket.socket: Connection socket
        """
        return self.connection
    
    def empty(self) -> bool:
        """If the message queue is empty

        Returns:
            bool: Yes if it is
        """
        return self.msg_queue.empty()