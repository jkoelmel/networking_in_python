import datetime
import pickle
import threading
from random import Random

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes

from menu import Menu


class ClientHandler:
    """
    The client handler class receives and process client requests
    and sends responses back to the client linked to this handler.
    """

    def __init__(self, server_instance, clientsocket, addr):
        """
        :param server_instance: passed as 'self' when the object of this class is created in the server object
        :param clientsocket: the accepted client on server side. this handler, by itself, can send and receive data
                             from/to the client that is linked to.
        :param addr: addr[0] = server ip address, addr[1] = client id assigned buy the server
        """
        self.server_ip = addr[0]
        self.client_id = addr[1]
        self.server = server_instance
        self.handler = clientsocket
        self.print_lock = threading.Lock()  # creates the print lock
        self.menu = Menu()
        self.username = ""
        self.messages = {}
        self.user_public_key = None
        self.chat_private_key = None
        self.chat_public_key = None
        self.chat_channel = {'channel': None, 'users': '', 'admin': ''}
        self.mapping = []
        self.mPrime = []
        self.names = ["", "Nick", "Bobby", "Mike"]

    def process_requests(self):
        """
        :return: VOID
        """
        while True:
            data = self.handler.recv(1024)
            if not data:
                break
            deserialized_data = pickle.loads(data)
            self.process_request(deserialized_data)

    def process_request(self, request):
        """
        :request: the request received from the client. Note that this must be already deserialized
        :return: VOID
        """
        option = request['headers']['option']

        response = {'payload': None, 'headers': {}, 'ack': -1}

        if option == 0:
            menu = self.menu.get()
            response = {'payload': menu, 'headers': {'clientid': self.client_id}, 'ack': 0}
            log = "Connected: \tUser: " + request['headers']['username'] + f"\tClient ID: {self.client_id}"
            self.username = request['headers']['username']
            self.log(log)
        elif option == 1:
            userList = self.get_users_connected()
            response = {'payload': userList, 'ack': 1}
        elif option == 2:
            message = request['payload']
            recipient = request['headers']['recipient']
            response['ack'] = self.save_messages(message, recipient)
        elif option == 3:
            response = {'payload': self.messages, 'ack': 3}
            self.messages = {}  # once read, clear messages list.
        elif option == 4:
            response = {'payload': None, 'ack': 4}
        elif option == 5:
            message = request['payload']
            response['ack'] = self.save_messages(message)
        elif option == 6:
            self.user_public_key = request['headers']['public_key']
            self.chat_channel['channel'] = request['headers']['channel']
            self.chat_channel['users'] = self.username
            self.chat_channel['admin'] = self.username
            key = RSA.generate(2048)
            self.chat_private_key = key.export_key()
            self.chat_public_key = key.public_key().export_key()
            recvKey = RSA.importKey(self.user_public_key)
            session_key = get_random_bytes(16)

            cipher_rsa = PKCS1_OAEP.new(recvKey)
            enc_session_key = cipher_rsa.encrypt(session_key)
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(self.chat_private_key)
            keyTransfer = []
            for item in (enc_session_key, cipher_aes.nonce, tag, ciphertext, self.chat_public_key):
                keyTransfer.append(item)
            response = {'payload': keyTransfer, 'ack': 6}
        elif option == 7:
            self.chat_channel['channel'] = request['headers']['channel']
            self.chat_channel['users'] = self.username
            self.user_public_key = request['headers']['public_key']
            key = RSA.generate(2048)
            self.chat_private_key = key.export_key()
            self.chat_public_key = key.public_key().export_key()
            recvKey = RSA.importKey(self.user_public_key)
            session_key = get_random_bytes(16)

            cipher_rsa = PKCS1_OAEP.new(recvKey)
            enc_session_key = cipher_rsa.encrypt(session_key)
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            ciphertext, tag = cipher_aes.encrypt_and_digest(self.chat_private_key)
            keyTransfer = []
            for item in (enc_session_key, cipher_aes.nonce, tag, ciphertext, self.chat_public_key):
                keyTransfer.append(item)
            userList = []
            for key, value in self.server.handlers.items():
                if value.chat_channel['channel'] == self.chat_channel['channel']:
                    userList.append(value.username)
                    if value.chat_channel['admin'] != '':
                        print("found admin!", value.chat_channel['admin'])
                        self.chat_channel['admin'] = value.chat_channel['admin']
            response = {'payload': keyTransfer, 'ack': 7, 'users': userList, 'admin': self.chat_channel['admin']}
        elif option == 8:
            response = {'payload': None, 'ack': 8, 'name': request['headers']['bot'], 'options': request['headers']['options']}
        elif option == 9:
            response = {'payload': self.mapping, 'ack': 9, 'names': self.names}
        elif option == 10:
            destination = []
            routes = []
            cost = []
            for i in range(1, len(self.names)):
                destination.append(self.names[i])
                routes.append([])
                cost.append(0)
            response = {'payload': self.mapping, 'ack': 10, 'names': self.names, 'destination': destination, 'routes': routes, 'cost': cost}
        elif option == 11:
            self.mPrime = self.mapping

            row = 0
            for j in range(1, len(self.names)):
                for k in range(j, len(self.names) - 1):
                    if j != k:
                        if (self.mapping[j][k] + self.mapping[0][k]) < self.mapping[0][k - 1]:
                            self.mPrime[row][k - 1] = self.mapping[j][k] + self.mapping[0][k]
                            self.mPrime[k - 1][row] = self.mPrime[row][k - 1]
                row += 1

            response = {'payload': self.mPrime, 'ack': 11, 'names': self.names, 'map': self.mapping}
        elif option == 12:
            response = {'payload': None, 'ack': 12}
        elif option == 13:
            self.server.handlers.pop((self.server_ip, self.client_id))
            self.log(f'{self.username} has disconnected.')
            response = {'payload': None, 'ack': 13}
        elif option == 100:
            # use user distances generated and populate rest of 2D matrix for 3 other users
            distances = request['payload']
            self.names[0] = self.username
            rand = Random()
            user2 = [distances[1], 0, 0, 0]
            user3 = [distances[2], 0, 0, 0]
            user4 = [distances[3], 0, 0, 0]
            self.mapping.append(distances)
            self.mapping.append(user2)
            self.mapping.append(user3)
            self.mapping.append(user4)

            # populate the rest of the distance map
            for i in range(4):
                for j in range(i):
                    self.mapping[i][j] = rand.randint(1, 20)
                    self.mapping[j][i] = self.mapping[i][j]

            response = {'payload': None, 'ack': 100}

        self.send(response)
        # after response is sent, if option 11 was chosen, update the mapping
        if option == 11:
            self.mapping = self.mPrime

    def get_users_connected(self):
        users = {}

        for key, value in self.server.handlers.items():
            users[value.username] = key[1]

        return users

    def save_messages(self, message, recipient=None):
        try:
            if not recipient:
                for key, value in self.server.handlers.items():
                    recipient_handler = self.server.handlers[key]

                    messages_list = recipient_handler.messages

                    if self.client_id not in messages_list.keys():
                        messages_list[self.client_id] = []

                    message_info = (datetime.datetime.now().replace(microsecond=0).isoformat(),
                                    message, f'broadcast message from {self.username}', self.client_id)

                    messages_list[self.client_id].append(message_info)

                return 5
            else:
                recipient_handler = None
                for key, value in self.server.handlers.items():
                    print(key, recipient)
                    if key[1] == recipient[1]:
                        recipient_handler = self.server.handlers[key]
                if recipient not in self.server.handlers.keys():
                    return -2

                messages_list = recipient_handler.messages

                if self.client_id not in messages_list.keys():
                    messages_list[self.client_id] = []

                message_info = (datetime.datetime.now().replace(microsecond=0).isoformat(),
                                message, f'private message from {self.username}')
                messages_list[self.client_id].append(message_info)
        except Exception as err:
            self.log(err)
            return -1

        return 2

    def send(self, data):
        """
        serializes and sends data to server on behalf of client
        """
        serialized_data = pickle.dumps(data)
        self.handler.send(serialized_data)

    def receive(self, max_mem_alloc=4096):
        """
        :max_mem_alloc: an integer representing the maximum allocation (in bytes) in memory allowed
                        for the data that is about to be received. By default is set to 4096 bytes
        :return: the deserialized data
        """
        deserialized_data = pickle.loads(self.handler.recv(1024))
        return deserialized_data

    def sendID(self, clientid):
        """
        sends clientID to client upon acceptance by server
        """
        message = {'clientid': clientid}
        self.send(message)

    def log(self, message):
        """
        log statement of connected persons to server console output
        """
        self.print_lock.acquire()
        print(message)
        self.print_lock.release()

    def run(self):
        self.process_requests()
