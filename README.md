# TCP/UDP Centralized Client-Server Network

## Project Template. 

This project template consist in two folders (Client and Server) and a requirements.txt file.

   * Client Folder
       1. client.py
       2. client_helper.py
       3. chat_bot.py
       4. chat_client.py
       5. udp_handler.py

   * Server Folder
        1. server.py
        2. client_handler.py 
        3. menu.py 
   * requirements.txt
        
   ***IMPORTANT: if needed, you can add more files to this project as its implementation progresses. However,
   you are not allowed to modify the code from client.py and server.py once you copied and pasted it from
   the labs. The only values students are allowed to modify in server.py are the IP address and port of the server***

## Project Requirements and Output Examples (***must read***)

The following are the guidelines you must follow to implement this project.

***IMPORTANT: in this README file when I refer to server or client, I am not referring to a particular file. I am, 
however, referring to all the files on those sides. To refer to a specific file, I will mention the name of the 
file. For example, server.py***

### Server

The server.py is the entry point file to execute the server for this app.

```
python server.py
```

Once the server is executed (assuming no errors), then the server must log in screen the following info about its
status. We assume here that the server is run from a machine on localhost and port 12000

```
Server is running without issues
Listening at 127.0.0.1/12000
```

### The Client

***Note that server and client are two independent applications in the same network and may be executed in different machines.
If you do not have access to a second machine, you can run both in the same machine (same IP address but different ports)***

To run the client (same machine or different machine than the server)

```
python client.py
```

Next, your program should show in screen the client's name and id assigned by the server. Similar to the following example

```
Enter the server IP Address: 127.0.0.1
Enter the server port: 12000
Enter a username: Nina
Successfully connected to server: 10.0.0.49/12000
Your client info is:
Client Name: Nina
Client ID: 50851
```

Note that the output "Successfully connected to server: 10.0.0.49/12000" must come from your client.py. The other
outputs (client name and client id) are printed out by the client_helper.py.

### The Menu

Even though the client side of this app is the one printing the menu for the user, the menu.py file that has all the
logic for the menu is located on the server side of this application.

```
****** TCP/UDP Network ******
------------------------------------
Options Available:
1.  Get users list
2.  Send a message 
3.  Get my messages 
4.  Send a direct message with UDP protocol
5.  Broadcast a message with CDMA protocol
6.  Create a secure channel to chat with your friends using PGP protocol
7.  Join an existing channel
8.  Create a Bot to manage a future channel
9.  Map the network
10. Get the Routing Table of this client with Link State Protocol
11. Get the Routing Table of this network with Distance Vector Protocol
12. Turn web proxy server on (extra-credit)
13. Disconnect from server

Your option <enter a number>:

```

### Menu options (explained)

Next, all the options from the menu are explained in detail with output examples.

#### Option 1: Get Users List
   
When users select this option the client helper sends a request to the server asking for a list of all the users connected to it.
The server sends that list, and the info from those users are shown in the client console. The info from the users connected
must be shown in the following format <username:client_id>.

Here is an example of the output needed for option #1
  
```
Your option <enter a number>: 1

Users connected: 4
Jarett:2345, Nina:8763, Alice:1234, Bob:4566
```

  
#### Option 2: Send a message

When this option is selected by the user, the client helper sends a request to the server containing the option selected,
from the menu, the message entered by the user, and the recipient id. When the client handler receives this requests,
it will need to find the client handler of the recipient of the message, and save the message there. After that,
the client handler (sender's handler) will send an acknowledgment response to the sender to let the
sender know that the message was received.

***Note that this is not a direct message method. The messages sent are saved on the server (client handler)
until the recipient requests them in option 3***

The following is an example of the output expected when the user selects option 2.

```
Your option <enter a number>: 2
Enter your message: Hello World!
Enter recipient id: 50922
Message sent!
```

***Note that the recipient's id is the client's id of the recipient of the message.***

#### Option 3: Get my messages

In this option, a user can request to the server all the unread messages sent from other users.

***IMPORTANT: only unread messages are included in the response.***

The following is an example of the expected output for option 3 where the user had 2 unread messages

```
Your option <enter a number>: 3

Number of unread messages: 2
2019-08-05 17:45: Hello World! (broadcast message from Nina)
2019-08-05 17:52: This is Bob. What are you doing? (private message from Bob)
```
#### Option 4: Send a direct message with UDP protocol

In this option, the message sent by the user is not saved on the list of messages in the client handler of the
recipient. It is, however, sent directly to the recipient in real time (one way only).

***IMPORTANT: When using this option. There is no way to know if the message arrived to its destination or was lost. Such is
the way of UDP***

Here is an example of the output expected when the user selects option 4.

```
Your option <enter a number>: 4

Enter the address to bind your UDP client (e.g 127.0.0.1:6000): 127.0.0.1:6000
Enter the recipient address: 127.0.0.1:6001
Enter the message: "This is a direct message. No guaranties that the message will arrive to its destination, but it's worth
the try"

UDP client running and accepting other clients at udp address 127.0.0.1:6000
Message sent to udp address: 127.0.0.1:6001
```

#### Option 5: Broadcast a message with CDMA protocol

When option 5 is selected by the user, the message entered by the user will be broadcast to all the users that
are connected to the network. Data is sent encoded by the server, and decoded on the client side using the CDMA protocol

Here is an example of the output expected when the user selects option 5. While looking simple to the end-user, the back-end
implementation is complete.

```
Your option <enter a number>: 5

Enter the message: "This is a direct broadcast message. Anyone out there?"

Message broadcast!.

```

#### Option 6: Create a secure channel to chat with your friends 

When option 6 is selected, it will create a ***SECURE*** channel for other users to join.

In order to create this channel, the user needs to input a channel id, and send the request to the server.

***Once the server receives the request, it will create public and private keys for that new channel with RSA.***

Once the secure channel has been created, the client is put in listening mode waiting for other members to join the chat.
(option 5). Only the owner/admin of the channel can close it by entering '#exit'. Once the channel is closed, 
the client console will show the user menu again.

Here is an example of the output expected when the user selects option 6.

```
Your option <enter a number>: 6

Enter the new channel id: 23456

Private key received from server and channel 23456 was successfully created!

----------------------- Channel 23456 ------------------------

All the data in this channel is encrypted

General Admin Guidelines:
1. #nina is the admin of this channel
2. Type '#exit' to terminate the channel (only for admins)


General Chat Guidelines:
1. Type #bye to exit from this channel. (only for non-admins users)
2. Use #<username> to send a private message to that user.

Waiting for other users to join....
```

#### Option 7: Join an existing channel

A user selecting option 7 will request to the server to be joined into an existing channel.

***IMPORTANT: when a new user joins a secure channel, the client will receive the public key of that channel sent 
by the server. The client of this user implements the PGP protocol to meet the security transmission
protocols established by the server***

Below is an example of the output that represents the joining process for several users

```
Your option <enter a number>: 7

Enter channel id you'd like to join: 23456

----------------------- Channel 23456 ------------------------

All the data in this channel is encrypted

jarett just joined
alice and #bob are already on the channel.
nina is the admin of this channel

Chat Guidelines:
Type #bye to exit from this channel. (only for non-admins)
Use #<username> to send a private message to that user.

alice> Hello jarett
jarett> Hello alice, who is the moderator of this chat?
nina> Hello alice, and jarett. I am the admin. How can I help you?
alice> Something came up and I gotta go. See you later guys!.
alice> #bye
alice left the channel.
bob> It looks like alice was in a hurry.
jarett> agree.
nina> Ok guys I got to go. Bye
nina> #exit

Channel 23456 closed by admin.


****** TCP/UDP Network ******
------------------------------------
Options Available:
1.  Get users list
2.  Send a message 
3.  Get my messages 
4.  Send a direct message with UDP protocol
5.  Broadcast a message with CDMA protocol
6.  Create a secure channel to chat with your friends using PGP protocol
7.  Join an existing channel
8.  Create a Bot to manage a future channel
9.  Map the network
10. Get the Routing Table of this client with Link State Protocol
11. Get the Routing Table of this network with Distance Vector Protocol
12. Turn web proxy server on (extra-credit)
13. Disconnect from server

Your option <enter a number>:
```

#### Option 8: Create a Bot to manage a future channel

When this option is selected, the system creates a bot to manage a future channel. Once a client sends a request
to the server to create a bot, the server will create a token for that bot. The token must be a SHA1 hash of a
concatenation of (1) the bot name and (2) the client id. This will make the bot's token unique among all the bots
created on the same server by other users.

After the server assigns a token to our new bot, it will send a response with all the disabled permissions that can be
enabled for the new bot. The user, then, will have to enter an integer representing the set of permissions that will
be instantiated for that bot. For example, if the user enters 145, the server will enable permissions 1, 4 and 5 for that bot.
(see the example output for more details about the permissions)

***Note that the bot you create in this option is for a future channel. You cannot create a bot for an existing channel because
it is not pipelined, and it works on the main thread. When a channel is created, it will scan for active bots created
by the admin of the channel, and will join them automatically***

The following is an example of the output for creating a bot

```
Your option <enter a number>: 8

Enter the name of your bot: MelindaBot

The disabled permissions for this bot are:
1. Welcome users right after they join a channel.
2. Show a warning to the users when they send words that are not allowed
3. Drop users from the channel after 3 warnings
4. Compute the response time of a message when the user request it
5. Inform the user when it has been inactive on the channel for more than 5 minutes.

Enter an integer to enable a set of permissions: 145

MelindaBot's Configuration:
Token: cf23df2207d99a74fbe169e3eba035e633b65d94
Permissions Enabled: 145
Status: ready
```

After a bot is set up and active, if we select option 7 to create a new channel, the channel will send a request
to the server to check if there are bots enabled owned by the admin of the channel, if so, then it will automatically join
them to the new channels and the bots will be able to perform the actions defined by their enabled permissions.

The following is a basic example of our new bot in a new channel:

```
----------------------- Channel 23456 ------------------------

All the data in this channel is encrypted

#melindaBot joined.
#jarett joined
#alice and #bob are already on the channel.
#nina is the admin of this channel

Chat Guidelines:
1. Type #bye to exit from this channel. (only for non-admins users)
2. Use #<username> to send a private message to that user.

melindaBot> Welcome #jarett.
jarett> I am wondering what's the response time of this message
melindaBot> jarett, the response time of your message is 0.01 milliseconds
melindaBot>> #alice you have been very quiet for the last five minutes. We miss you!

```
#### Option 9: Get the Routing Table of this client with Link State Protocol

In this option the server will map the network upon client request. If one or more clients are running in the same machine, 
then the server will assign random distances to those clients.

The following is an example of the output needed for this option:

```
Your option <enter a number>: 9

Routing table requested! Waiting for response.... 

Network Map: 

         |  Nina   |  Alice  |   Jarett     |    Bob      |
-----------------------------------------------------------
Nina     |   0     |    15   |     10       |     -       |
Alice    |   15    |    0    |     30       |     11      |
Jarett   |   10    |    30   |     0        |     25      |
Bob      |   -     |    11   |     25       |     0       |
```
 
#### Option 10: Get the Routing Table of this client with Link State Protocol

In this option the client will request its routing table to the server using itself as the source node. Then the 
client will print the routing table for the user.  

A map of the network must be printed (implementation of option 9) and next the routing table. This way, it is easy
to check if the server made mistakes with the computations of the shortest distances. 

The following is an example of the output needed for this option:

```
Your option <enter a number>: 10

Routing table requested! Waiting for response.... 

Network Map: 

         |  Nina   |  Alice  |   Jarett     |    Bob      |
-----------------------------------------------------------
Nina     |   0     |    15   |     10       |     -       |
Alice    |   15    |    0    |     30       |     11      |
Jarett   |   10    |    30   |     0        |     25      |
Bob      |   -     |    11   |     25       |     0       |

Routing table for Nina (id: 50851) computed with Link State Protocol: 

|  destination |              Path                 |      Cost      | 
-------------- | --------------------------------  | -------------  |
|    Alice     |          {Nina, Alice}            |       15       |
|   Jarett     |        {Nina, Jarett  }           |       10       |
|     Bob      |      {Nina, Jarett  , Bob}        |       35       |
```

#### Option 11: Get the Routing Table of this network with Distance Vector Protocol

The implementation of this option is similar to the one from option 10. However, in this case and after computing/updating
the map of the network, the server will compute the routing table for this client using the Distance Vector Protocol.

***IMPORTANT: the routing table received from the server is the same routing table for all the clients because the
Distance Vector protocol determines the shortest path from all the pair of nodes in the network***

The following is an example of the output. We assume here that Bob disconnected from the network:

```
Your option <enter a number>: 11

Routing table requested! Waiting for response.... 

Network Map: 

         |  Nina   |  Alice  |   Jarett     |
---------------------------------------------
Nina     |   0     |    2    |      7       |    
Alice    |   2     |    0    |      1       |     
Jarett   |   7     |    1    |      0       |     


Routing table computed with Distance Vector Protocol: 

         |  Nina   |  Alice  |   Jarett     |
---------------------------------------------
Nina     |   0     |    2    |      3       |    
Alice    |   2     |    0    |      1       |     
Jarett   |   3     |    1    |      0       |     
```

As you can see in the routing table, some distances were updated to reflect the shortest path 
between nodes. 

#### Option 12: Turn web proxy server on (WIP)


#### Option 13: Disconnect from server

A user selecting this option will request to be disconnected from the server. The client sends the request to the server, then the server performs a cleanup of all the data related to that client in the server, and finally close the connection with that client socket. In addition, you also have the option to disconnect the client on the client side. Although this may work just fine, it is more prone to errors since the server still needs to do the cleanup of data for that socket (which do not exist anymore). 


# Running the project, 

You must follow exactly these instructions in order to run and test your project. If I cannot run your project, 
as the following guidelines state, you'll get a zero in this project. No exceptions here!. So, test it properly before final submission. 

To run the server:

``` 
python3 server.py 
```
***IMPORTANT: the server can run in localhost, or it can run using the IP address was assigned by your LAN to the machine 
running the server. If you set the IP address of the server to '0.0.0.0' the server socket will bind the LAN IP address assigned to 
that machine to the program and the port provided by the programmer in the server.py code***

To run a client, you have two options:

1. Run clients in different machines (LAN)
2. Run clients in the same machine as your server (localhost)

``` 
python3 client.py 
```
