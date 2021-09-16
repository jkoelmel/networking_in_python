import socket
import pickle
import time
from threading import Thread
from Crypto.Hash import SHA1
from pythonping import ping


class Bot:

    def __init__(self, port, options=None, botName=None):
        self.addr = ''
        self.port = int(port)
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.badWords = ['ass', 'asshole', 'shit', 'fuck', 'dick', 'bastard', 'retard', 'whore']
        self.user = botName
        self.options = []
        self.warnCount = []
        self.messageTracker = []
        self.found = False
        hashed = SHA1.new()
        hashed.update(self.user.encode('utf-8'))
        for option in options:
            self.options.append(int(option))
        print(f"{self.user}'s Configuration:")
        print("Token:", hashed.hexdigest())
        print("Permissions enabled:", options)
        print("Status: ready")

    def receive(self):
        while True:
            data, address = self.udpSocket.recvfrom(1024)
            deserialized_data = pickle.loads(data)
            self.found = False
            for i in range(len(self.warnCount)):
                if self.found:
                    break
                elif self.warnCount[i][0] == address[0]:
                    self.found = True
                    break
            if not self.found:
                self.warnCount.append([address[0], 0])
            for word in deserialized_data['message'].split(' '):
                if deserialized_data['message'].split(' ')[0] == f'>{self.user}':
                    break
                elif deserialized_data['message'][-6:] == 'joined' and 1 in self.options:
                    hashed = SHA1.new()
                    msg = 'Welcome to the channel!'
                    msg = f'>{self.user} ' + msg
                    hashed.update(msg.encode('utf-8'))
                    messageAndHash = {'hash': hashed.hexdigest(), 'message': msg}
                    self.broadcast(pickle.dumps(messageAndHash))
                    self.messageTracker.append([address, time.perf_counter()])
                    break
                elif word in self.badWords and 2 in self.options:
                    hashed = SHA1.new()
                    msg = "You cant say that here!"
                    msg = f'>{self.user} ' + msg
                    hashed.update(msg.encode('utf-8'))
                    messageAndHash = {'hash': hashed.hexdigest(), 'message': msg}
                    self.broadcast(pickle.dumps(messageAndHash))
                    if 3 in self.options:
                        for i in range(len(self.warnCount)):
                            if address[0] in self.warnCount[i]:
                                self.warnCount[i][1] += 1
                                if self.warnCount[i][1] >= 3:
                                    hashed = SHA1.new()
                                    msg = "You have been banned from the server"
                                    msg = f'>{self.user} ' + msg
                                    hashed.update(msg.encode('utf-8'))
                                    messageAndHash = {'hash': hashed.hexdigest(), 'message': msg}
                                    self.broadcast(pickle.dumps(messageAndHash))
                elif 'compute' and 'response' in deserialized_data['message'].split(' ') and 4 in self.options:
                    r = ping(address[0])
                    hashed = SHA1.new()
                    msg = f'Avg RTT for you is {r.rtt_avg/2} seconds'
                    msg = f'>{self.user} ' + msg
                    hashed.update(msg.encode('utf-8'))
                    messageAndHash = {'hash': hashed.hexdigest(), 'message': msg}
                    self.broadcast(pickle.dumps(messageAndHash))
                    break
                if 5 in self.options:
                    for j in range(len(self.messageTracker)):
                        if address in self.messageTracker[j]:
                            if (time.perf_counter() - self.messageTracker[j][1]) > 300:
                                hashed = SHA1.new()
                                msg = "You have been gone over 5 minutes, consider disconnecting"
                                msg = f'>{self.user} ' + msg
                                hashed.update(msg.encode('utf-8'))
                                messageAndHash = {'hash': hashed.hexdigest(), 'message': msg}
                                self.broadcast(pickle.dumps(messageAndHash))
                                break
                            else:
                                self.messageTracker[j][1] = time.perf_counter()
                                break
                    # if user not found, default case, should be appended when connecting though
                    self.messageTracker.append([address, time.perf_counter()])

    def listen(self):
        self.receive()

    def broadcast(self, msg, toItself=False):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # set socket to broadcast with flag
        sock.sendto(msg, ('<broadcast>', self.port))
        if toItself:
            self.listen()

    def run(self):
        print(f'\n#{self.user} has joined the chat\n')
        thread = Thread(target=self.listen)
        thread.start()

    def setPort(self, port):
        self.port = port
        self.udpSocket.bind((self.addr, int(self.port)))
