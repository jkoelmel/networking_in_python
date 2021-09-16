import json
import pickle
import sys
import time

from threading import Thread
from random import Random
from bitarray import bitarray
from bitarray.util import hex2ba, ba2hex
from chat_bot import Bot
from udp_handler import Tracker
from chat_client import Chat
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


class ClientHelper:

    def __init__(self, client):
        self.client = client
        self.client_id = -1
        self.username = ""
        self.menu_table = {}
        self.connected = False
        self.option = -1
        self.udp_tracker = None
        self.udp_binding = ()
        self.keys = RSA.generate(2048)
        self.chat_channel = None
        self.private_key = None
        self.public_key = None
        self.chat_private_key = None
        self.chat_public_key = None
        self.bot = None
        self.botPresent = False
        self.botName = ''
        self.botOptions = ''

    def create_request(self, option=0):
        """
        :return: the created request
        """
        request = {'payload': None, 'headers': {}}
        if option == 0 and not self.connected:  # Even though logic checks are performed elsewhere this is just a backup
            # initial connection request
            request = {'payload': None, 'headers': {'option': 0, 'username': self.username}}
            return request
        elif option == 1:
            request = {'payload': None, 'headers': {'option': 1}}
            return request
        elif option == 2:
            # create a request using the message and recipient
            message = input('Enter your message: ')
            recipient = int(input('Enter recipient id: '))
            request = {'payload': message,
                       'headers': {'option': 2, 'recipient': ('127.0.0.1', recipient)}}
            return request
        elif option == 3:
            request = {'payload': None, 'headers': {'option': 3}}
        elif option == 4:
            binding = tuple(input("Enter the address to bind your UDP client (e.g. 127.0.0.1:9000): ").split(':'))
            recipient = tuple(input("Enter the recipient address: ").split(':'))
            message = input("Enter the message: ")
            serialized_message = pickle.dumps(message)
            if not self.udp_tracker:
                self.udp_binding = binding
                self.udp_tracker = Tracker(self.udp_binding)
            else:
                print(f'User has UDP client bound to {self.udp_binding}')
            self.udp_tracker.send(serialized_message, recipient)
            Thread(target=self.udp_handler(self.udp_tracker)).start()
            request = {'payload': None, 'headers': {'option': 4}}
        elif option == 5:
            message = input("Enter message: ")
            bit_message = self.cdma_encode(message)
            request = {'payload': bit_message, 'headers': {'option': 5}}
        elif option == 6:
            channel = 0
            while int(channel) < 100 or int(channel) > 65000:
                channel = input("Enter the new channel ID: ")
                self.chat_channel = channel
            self.private_key = self.keys.export_key()
            self.public_key = self.keys.public_key().export_key()
            request = {'payload': None, 'headers': {'option': 6, 'channel': self.chat_channel, 'public_key': self.public_key}}
        elif option == 7:
            channel = 0
            while int(channel) < 100 or int(channel) > 65000:
                channel = input("Enter the new channel ID: ")
                self.chat_channel = channel
            self.private_key = self.keys.export_key()
            self.public_key = self.keys.public_key().export_key()
            request = {'payload': None, 'headers': {'option': 7, 'channel': self.chat_channel, 'public_key': self.public_key}}
        elif option == 8:
            name = input("Enter the name of your bot: ")

            print('\nThe available permissions of this bot are:\n1. Welcome Users right after they join the channel.')
            print('2. Show a warning to the user when they send words not allowed\n3. Drop users from the channel after 3 warnings')
            print('4. Compute response time of a message when the user requests it\n5. Inform the user when it has been inactive for 5 minutes\n')

            options = input("Enter integers (no spaces) to enable permission for bot: ")

            request = {'payload': None, 'headers': {'option': 8, 'bot': name, 'options': options}}
        elif option == 9:
            request = {'payload': None, 'headers': {'option': 9}}
            print("\nRouting table requested, waiting for response....\n\n")
        elif option == 10:
            request = {'payload': None, 'headers': {'option': 10}}
            print("\nLink state table requested, waiting for response....\n\n")
        elif option == 11:
            request = {'payload': None, 'headers': {'option': 11}}
            print("\nDistance vector table requested, waiting for response....\n\n")
        elif option == 12:
            request = {'payload': None, 'headers': {'option': 12}}
        elif option == 13:
            # disconnect from server
            request = {'payload': None, 'headers': {'option': 13}}
        return request

    def send_request(self, request):
        """
        :request: a request representing deserialized data.
        """
        self.client.send(request)

    def process_response(self):
        """
        :response: the serialized response.
        """
        data = self.client.receive()
        # print(data)
        if not self.connected and 'clientid' in data['headers']:
            self.connected = True
            self.client_id = data['headers']['clientid']
            print(
                "Your client info:\nClient Name: {}\nClient ID: {}".format(self.username, data['headers']['clientid']))
            distances = self.update_table()
            request = {'payload': distances, 'headers': {'option': 100}}
            self.send_request(request)
            self.process_response()
        if data['ack'] == 0:
            menu = data['payload']
            self.menu_table = json.loads(menu)
        if data['ack'] == 1:
            print('\n')
            for key, value in data['payload'].items():
                print(f'{key}:{value}', sep=',')
        elif data['ack'] == 2:
            print("Message sent!")
        elif data['ack'] == -2:
            print("User is not available to message")
        elif data['ack'] == 3:
            missed_messages = 0
            for key, value in data['payload'].items():
                missed_messages = missed_messages + len(value)
            if not data['payload']:
                print('You have no new messages')
                return
            else:
                print(f'Number of unread messages: {missed_messages}')
            for message_list in data['payload'].values():
                for message in message_list:
                    if isinstance(message[1], bitarray):
                        decoded_message = self.cdma_decode(message[1], message[3])
                        date_time = message[0].split("T")
                        print(f'{date_time[0]} {date_time[1]}: {decoded_message}  ({message[2]})')
                        continue
                    else:
                        date_time = message[0].split("T")
                        print(f'{date_time[0]} {date_time[1]}: {message[1]}  ({message[2]})')
        elif data['ack'] == 4:
            pass
        elif data['ack'] == 5:
            print("Message broadcast!")
        elif data['ack'] == 6:
            nonce = data['payload'][1]
            enc_session = data['payload'][0]
            cipherRSA = PKCS1_OAEP.new(RSA.import_key(self.private_key))
            session = cipherRSA.decrypt(enc_session)
            cipherAES = AES.new(session, AES.MODE_EAX, nonce)
            key = cipherAES.decrypt_and_verify(data['payload'][3], data['payload'][2])
            self.chat_private_key = key
            self.chat_public_key = data['payload'][4]
            print(f'\nPrivate key rec\'v from server and channel {self.chat_channel[1]} was created!')
            chat = Chat(self.chat_channel, self.username, data['payload'], True)
            thread = None
            if self.botPresent:
                self.bot.setPort(int(self.chat_channel))
                thread = Thread(target=self.bot.run)
                thread.start()
            self.udp_handler(chat)
            if thread:
                thread.join(0.25)
                self.bot.udpSocket.close()
        elif data['ack'] == 7:
            nonce = data['payload'][1]
            enc_session = data['payload'][0]
            cipherRSA = PKCS1_OAEP.new(RSA.import_key(self.private_key))
            session = cipherRSA.decrypt(enc_session)
            cipherAES = AES.new(session, AES.MODE_EAX, nonce)
            key = cipherAES.decrypt_and_verify(data['payload'][3], data['payload'][2])
            self.chat_private_key = key
            self.chat_public_key = data['payload'][4]
            chat = Chat(self.chat_channel, self.username, data['payload'], False, data['users'], data['admin'])
            self.udp_handler(chat)
        elif data['ack'] == 8:
            print("\n\n")
            self.botPresent = True
            self.botName = data['name']
            self.botOptions = data['options']
            self.bot = Bot(int(9000), self.botOptions, self.botName)
        elif data['ack'] == 9:
            mapping = data['payload']
            names = data['names']
            i = 0
            print('---------- Network Map ----------\n\n')
            print("Mapping", end='\t\t\t')
            for name in names:
                print('{:^10s}'.format(name), end='\t\t')
            print('\n')
            for row in mapping:
                print(names[i], end='\t\t|')
                for col in row:
                    print('\t\t{}'.format(col), end='\t\t|')
                print('\n')
                i += 1
        elif data['ack'] == 10:
            mapping = data['payload']
            names = data['names']
            destination = data['destination']
            routes = data['routes']
            cost = data['cost']

            for i in range(len(names)-1):
                cost[i] = mapping[0][i + 1]
                routes[i] = [destination[i]]

            for j in range(1, len(names)):
                currentCost = cost[j - 1]
                for k in range(j, len(names) - 1):
                    if (mapping[j][k + 1] + mapping[0][k]) < currentCost:
                        temp = routes[j - 1].pop()
                        routes[j - 1].append(names[j + 1])
                        routes[j - 1].append(temp)
                        cost[j - 1] = mapping[j][k + 1] + mapping[0][k]

            titles = ['Destination', 'Path', 'Cost']
            print(f'Routing table for {self.username} (id:{self.client_id}) computed with Link State Protocol\n')
            for title in titles:
                print('\t{:^20s}'.format(title), end='\t|')
            print('\n')
            for i in range(len(destination)):
                print('\t{:^20s}'.format(destination[i]), end='\t|')
                print('\t{:^20s}'.format(str(routes[i])), end='\t|')
                print('\t{:^20d}'.format(cost[i]), end='\t|')
                print('\n')
        elif data['ack'] == 11:
            mapping = data['map']
            names = data['names']
            mPrime = data['payload']
            i = 0

            print('---------- Network Map ----------\n\n')
            print("Mapping", end='\t\t\t')
            for name in names:
                print('{:^10s}'.format(name), end='\t\t')
            print('\n')
            for row in mapping:
                print(names[i], end='\t\t|')
                for col in row:
                    print('\t\t{}'.format(col), end='\t\t|')
                print('\n')
                i += 1

            i = 0
            print('Routing table computed with DVP:\n')
            print("Mapping", end='\t\t\t')
            for name in names:
                print('{:^10s}'.format(name), end='\t\t')
            print('\n')
            for row in mPrime:
                print(names[i], end='\t\t|')
                for col in row:
                    print('\t\t{}'.format(col), end='\t\t|')
                print('\n')
                i += 1
        elif data['ack'] == 12:
            print("Might you consider a subscription to ExpressVPN today?")
        elif data['ack'] == 13:
            print("Closing connection...")
        elif data['ack'] == 100:
            print('Distance values updated in server...')
        elif data['ack'] == -1:
            print("Something went wrong, please try again...")

    @staticmethod
    def print_menu(menu):
        print("\n\n")
        for heading in menu['titles']:
            print(heading)
        for option, title in menu['options'].items():
            print(option + ": " + title)

        option = int(input("\n\nOption <Enter a number>: "))
        while option not in range(1, 14):
            option = int(input("\nInvalid entry, choose another option:"))

        return option

    @staticmethod
    def udp_handler(tracker):
        tracker.run()

    def cdma_encode(self, message):
        # standard 4-channel orthogonal codes from generic walsh table
        codes = [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]
        userCode = codes[(self.client_id % 4)]
        encoded_message = message.encode('utf-8')
        raw_data = bitarray(hex2ba(encoded_message.hex()))
        expanded_data = bitarray()
        for bit in raw_data:
            for i in range(4):
                expanded_data.append(bit)

        expanded_code = bitarray(bitarray(userCode) * len(encoded_message) * 8)
        encrypted_message = expanded_code ^ expanded_data
        return encrypted_message

    @staticmethod
    def cdma_decode(message, sender_id):
        codes = [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]
        userCode = codes[(sender_id % 4)]
        length = (len(message) // 4)
        decryption_code = bitarray(bitarray(userCode) * length)
        decrypted_stream = message ^ decryption_code
        compressed_data = decrypted_stream[0::4]
        message = ba2hex(compressed_data)
        message = bytes.fromhex(message).decode('utf-8')
        return message

    ''' data from routing table is simulated for 3 users other than current
    this was done to expedite testing and minimize the need for VM instances

    the rest of the table is simulated by the server so that link state and routing
    tables can be computed
    '''
    @staticmethod
    def update_table():
        distance = [0]
        for i in range(3):
            rand = Random()
            distance.append(rand.randint(1, 30))
        return distance

    def start(self):
        """
        initialize process for ClientHelper
        """
        self.username = input("Enter a username: ")

        # used for quicker debugging
        # self.username = "Jarett"

        request = self.create_request()
        self.send_request(request)
        self.process_response()
        while self.option != 13:
            self.option = self.print_menu(self.menu_table)
            request = self.create_request(self.option)
            self.send_request(request)
            self.process_response()

        self.client.close()
        time.sleep(2)
        sys.exit()
