import socket
import time
from threading import Thread
import pickle
from Crypto.Hash import SHA1


class Chat:

    def __init__(self, address, user, keyTransfer, admin=False, userlist=None, nameOfAdmin=None):
        self.addr = ''
        self.port = int(address)
        self.user = user
        self.userIP = None
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # used to bypass single machine testing
        self.udpSocket.bind((self.addr, self.port))
        self.admin = admin
        self.adminUser = nameOfAdmin
        if self.admin:
            self.adminUser = self.user
        self.keys = keyTransfer
        self.userList = userlist
        self.DM = []

    def send(self, msg, address):
        self.udpSocket.sendto(msg, address)  # address is IP/port tuple

    def receive(self):
        while True:
            try:
                data, address = self.udpSocket.recvfrom(1024)
                deserialized_data = pickle.loads(data)
                if not self.userIP:
                    self.userIP = address[0]
                    self.DM.append(deserialized_data['message'].split(' ')[0][0:])
                    self.DM.append(address[0])
                recvHash = SHA1.new()
                recvHash.update(deserialized_data['message'].encode('utf-8'))
                if recvHash.hexdigest() == deserialized_data['hash']:
                    print(deserialized_data['message'])
                else:
                    print("Recent message corrupted en route")
            except socket.error:
                pass

    def listen(self):
        self.receive()

    def broadcast(self, msg, toItself=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # set socket to broadcast with flag
        sock.sendto(msg, ('<broadcast>', self.port))
        if toItself:
            self.listen()

    def run(self):
        if self.admin:
            print(f"\n---------- Channel {self.port} ----------\n")
            print('All the data in this channel is encrypted\n')
            print(f'General Admin Guidelines:\n1. #{self.adminUser} is the admin of this channel\n')
            print('2. Type "#exit" to terminate the channel (only for admins)\n\n')
            print('General Chat Guidelines:\n1. Type #bye to exit from this channel. (non admins)\n')
            print('2. Use #<username> to send a private message to that user\n')
            print('Waiting for other users to join.....')
            thread = Thread(target=self.listen)
            thread.start()
            while True:
                message = input(">")
                if message == '#exit':
                    hashed = SHA1.new()
                    exitMessage = f"Channel {self.port} closed by admin.\n"
                    hashed.update(exitMessage.encode('utf-8'))
                    messageAndHash = {'hash': hashed.hexdigest(), 'message': exitMessage}
                    self.broadcast(pickle.dumps(messageAndHash))
                    thread.join(0.25)
                    self.udpSocket.close()
                    break
                elif message == '':
                    continue
                elif message[0] == "#":
                    print(self.DM)
                    count = 0
                    for user in self.DM:
                        if message.split(' ')[0] == ('#' + str(user)):
                            try:
                                print(count)
                                receiverIP = self.DM[count+1]
                                hashed = SHA1.new()
                                message = f'{self.user}> ' + message
                                hashed.update(message.encode('utf-8'))
                                messageAndHash = {'hash': hashed.hexdigest(), 'message': message}
                                self.send(pickle.dumps(messageAndHash), receiverIP)
                            except Exception as error:
                                print('User not found', error)
                                continue
                        count += 1
                else:
                    hashed = SHA1.new()
                    message = f'{self.adminUser}> ' + message
                    hashed.update(message.encode('utf-8'))
                    messageAndHash = {'hash': hashed.hexdigest(), 'message': message}
                    self.broadcast(pickle.dumps(messageAndHash))
        else:
            print(f"\n---------- Channel {self.port} ----------\n\n")
            print('All the data in this channel is encrypted\n\n')
            print(f'{self.adminUser} is the admin of this chat\n')
            for user in self.userList:
                if len(self.userList) == 1:
                    print(user, "is only user other than admin in this chat\n")
                elif user == self.userList[-1]:
                    print(f' and {user} are currently in this chat\n')
                else:
                    print(user, end=',')

            message = ' just joined'
            self.sendWithHash(self.user, message)
            time.sleep(1)
            print('\nChat Guidelines:\nType #bye to exit from this channel (non admins)\n')
            print('Use #<username> to send a private message to that user\n\n')
            thread = Thread(target=self.listen)
            thread.start()

            while True:
                hashed = SHA1.new()
                message = input(">")
                if message == "#bye":
                    exitMessage = 'has left the channel\n'
                    self.sendWithHash(self.user, exitMessage)
                    thread.join(0.25)
                    self.udpSocket.close()
                    break
                elif message == '':
                    continue
                elif message[0] == "#":
                    print(self.DM)
                    count = 0
                    for user in self.DM:
                        if message.split(' ')[0] == ('#' + str(user)):
                            try:
                                print(count)
                                receiverIP = self.DM[count+1]
                                message = f'{self.user}> ' + message
                                hashed.update(message.encode('utf-8'))
                                messageAndHash = {'hash': hashed.hexdigest(), 'message': message}
                                self.send(pickle.dumps(messageAndHash), receiverIP)
                            except Exception as error:
                                print('User not found', error)
                                continue
                        count += 1
                else:
                    self.sendWithHash(self.user, message)

    def sendWithHash(self, user, message):
        hashed = SHA1.new()
        message = f'{user} ' + message
        hashed.update(message.encode('utf-8'))
        messageAndHash = {'hash': hashed.hexdigest(), 'message': message}
        self.broadcast(pickle.dumps(messageAndHash))