import sys
from .message import Message,print_msg
from .network import Network
from tabulate import tabulate

class Input:
    def __init__(
        self,
        network:Network) -> None:
        """This deals with the input provided by user

        Args:
            network (Network): The network details associated with peer
        """ 
        self.network = network
        
    def fileno(self) -> int:
        """Used by select to know which file descriptor is being used

        Returns:
            int: file descriptor
        """
        return sys.stdin.fileno()
    
    def on_read(self):
        """A function that will be called when the input stream has something to read
        """
        usr_input = sys.stdin.readline().strip()
        
        # get the command user wants to perform
        cmd = usr_input.split()[0]
        
        # print all the connection
        if cmd == "list":
            self.print_in(tabulate(list(self.network.get_network_servers().items()),headers=["id","port"]))
            
        # print your port
        elif cmd == "myport":
            self.print_in(self.network.get_port())
            
        # print leader info
        elif cmd == "leader":
            self.print_in(f"id : {self.network.get_leader_id()}")
            self.print_in(f"port : {self.network.get_leader_port()}")
            
        # broadcast message to all peers
        elif cmd == "broadcast":
            self.broadcast(usr_input)
            
        # send message to a specific peer
        elif cmd == "send":
            self.send(usr_input)
            
        # display help window
        elif cmd == "help":
            self.print_commands()
            
        # Close the current peer
        elif cmd == "terminate":
            self.network.terminate()
        
        # print unrecognisabe to all other
        else:
            self.print_in("Unrecognisable")
    
    def send(self,usr_input:str):
        """Used for sending message to a peer

        Args:
            usr_input (str): the prompt provided by the user
        """
        
        # get the peer id to send message to
        send_to = int(usr_input.split()[1])
        
        # check if there is a message to send
        if len(usr_input.split())<3:
            print_msg("No message entered")
            return
        
        # create a message and add it for sending
        to_send = Message(
            sender_id = self.network.get_id(),
            reciever_id = send_to,
            msg_type = "GENERAL",
            msg = " ".join(usr_input.split()[2:])
        )
        self.network.add_send_request(send_to,to_send)
        
    def broadcast(self,usr_input:str):
        """Send a message to all the peers

        Args:
            usr_input (str): The prompt provided by user
        """
        if len(usr_input.split())<2:
            self.print_in("No message entered")
            return
        
        """Create a message and ask the network to broadcast it"""
        to_send = Message(
            sender_id = self.network.get_id(),
            reciever_id = "all",
            msg_type = "GENERAL",
            msg = " ".join(usr_input.split()[1:])
        )
        self.network.broadcast(to_send)
        
    def print_in(self,x:str):
        """A function to print messages

        Args:
            x (str): string
        """
        print(f"\n{x}",end="")
        
    def print_commands(self):
        """Print all the available commands
        """
        data = {
            "list": "lists all the peers",
            "myport": "Tells running port",
            "leader": "Tells id and port of leader",
            "broadcast": "[msg] Sends message to all peer",
            "send": "[send_to] [msg] Sends message msg to send to",
            "terminate": "Disconnects the peer",
            "help": "prints help menu"
        }
        self.print_in(tabulate(list(data.items()),headers=["commands","usage"]))