import json
from constants import FORMAT,VERBOSE

class Message:
    def __init__(self,bts:bytes=None,**kwargs) -> None:
        """A helper fuction to deal with messages

        Args:
            bts (bytes, optional): Recieved message. Defaults to None.
        """
        
        # if fessage is in bytes then decode it
        if bts is not None:
            self.msg = json.loads(bts.decode(FORMAT))
            
        # otherwise build the message using the kwargs
        else:
            self.msg = kwargs
            
        # get the sender and reciever id
        self.sender_id = self.msg.get('sender_id')
        self.reciever_id = self.msg.get("reciever_id")
        
    def display(self):
        """Displays the message
        """
        self.print_msg(f"{self.sender_id} :: {self.msg['msg']}")
        
    def display_sent(self):
        """Displays what you sent
        """
        self.print_msg(f"Sent {self.msg['msg']} to {self.reciever_id}")
        
    def update_reciever(self,new_id:int):
        """Used to update the reciever of the message

        Args:
            new_id (int): id to update it with
        """
        self.reciever_id = new_id
        self.msg['reciever_id'] = new_id
        
    def get_msg(self)->dict:
        """Get the actual message

        Returns:
            dict: Dictionary of message
        """
        return self.msg
    
    def is_ping(self) -> bool:
        """If the message is ping

        Returns:
            bool: True if it is
        """
        return self.get_msg_type() == "PING"
    
    def is_pong(self) -> bool:
        """If the message is pong

        Returns:
            bool: True if it is
        """
        return self.get_msg_type() == "PONG"
    
    def is_win(self) -> bool:
        """If the message is for election win

        Returns:
            bool: True if it is
        """
        return self.get_msg_type() == "WIN"
    
    def is_campaign(self) -> bool:
        """If the message is for election campaign

        Returns:
            bool: True if it is
        """
        return self.get_msg_type() == "CAMPAIGN"
    
    def is_election(self) -> bool:
        """If the message is either election or win

        Returns:
            bool: True if it is
        """
        return self.is_win() or self.is_campaign()
    
    def get_msg_type(self)->str:
        """Type of the crrent message

        Returns:
            str: The message type
        """
        return self.msg['msg_type']
    
    def get_msg_buff(self)->bytes:
        """Encode the current message to send

        Returns:
            bytes: Message encoding
        """
        return json.dumps(self.msg).encode(FORMAT)
    
    def print_msg(self,msg:str):
        """Util for printing message

        Args:
            msg (str): the text to print
        """

        print(f"\n{msg} ",end="")
    
def print_msg(msg:str):
    """Util for printing message

        Args:
            msg (str): the text to print
        """
    if VERBOSE:
        print(f"\n{msg} ",end="")