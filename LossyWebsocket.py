"""
This module implements a client websocket that looses messages with some probablity. 


Created: 10.12.25
Written by Marcus Venzke, NCPS, TUHH
"""
import random 
from websockets.asyncio import client

# Probability that a message is lost when it is sent or received. 
# Allowed values are between 0.0 and 1.0.
lossProbability = 0.1
# lossProbability = 0.0 # No loss for testing. 


class LossyClientConnection:
    def __init__(self, originalClientConnection): 
        """
        Object wrapping the lossy client connection. 
        Parameter originalClientConnection is the websocket client connection 
                  that does not lose messages. 
        """
        self.connection = originalClientConnection 
        self.lossProbability = lossProbability 
    
    
    async def send(self, message): 
        """
        Sends the message to a websocket given as parameter or does nothing. 
        The probability for not sending is lossProbability. 
        The probability for sending is 1-lossProbability.
        Parameter message: Message to be sent. 
        """
        if not (random.random() <= lossProbability): # If message is not lost ... 
            await self.connection.send(message)          # then send the message. 
    
    
    async def recv(self):
        """
        Receives a message from a websocket. While doing so, it might loose messages. 
        The probablility for loosing the received message is lossProbability. 
        If a message is lost, then the function waits until the next message receives. 
        Returns the received message. 
        """
        while True: # Repeat until a message is returned. 
            message = await self.connection.recv()  # (Reliabliy) Receive the next message
            if not (random.random() <= lossProbability): # If message is not to be lost ...  
                return message
                
                
async def connect(uri): 
    """
    Connects to a websocket server and 
    """
    return LossyClientConnection(await client.connect(uri))