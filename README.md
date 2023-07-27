# Chat-app
This program allows user to have a peer to peer chat with each other along with option for broadcast. It uses leadership election to choose the leadeer. A new node can be added by pinging the leader.

## About
This program emulates a peer to peer chat app to simulate a leader election algorithm<br>
The importance of leader in the app is
- A new peer should always connect to leader first
- If the leader is lost then a new one is elected based on the consensus algorithm
- Currently the following algorithms have been added:
    - BullyAlgorithm
    - Paxos
    - Raft
    - TCPBasedConnectionElection
- The 
- More consensus algorithm can be added in such a way
    - The algorithm should take the network as parameter
    - It must implement the following methods
        - process_election_message(Message) : Gets called when an elction message is recieved
        - check_win() : Gets called every 1s or whenever there is a state change
        - start_slection() : Function to run to start election

This program has been tested on PopOS! and will work on any linux distro. Every peer in this network only uses one thread by employing the select method provided in linux. This makes the program highly scalable. The software uses socket so it can be easily extended for internet based communication. <br>
The chat app is highly reliable as it uses TCP connection to send the messages

## setup
First start a genesis node by using
```
python3 main.py [PORT]
```
Ask for the leader port at this peer using
```
leader
```
Add multiple peers to this cluster by using
```
python3 main.py [LEADER_PORT] [PORT]
```
