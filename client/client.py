import pickle
import socket
import sys

from client_helper import ClientHelper


class Client(object):

    def __init__(self):
        """
        Class constructor
        """
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.id = 0

    def connect(self, server_ip_address, server_port):
        """
        :server_ip_address: the known ip address of the server
        :server_port: the port of the server
        """
        try:
            self.client.connect((server_ip_address, server_port))
        except (OSError, ConnectionError, ConnectionResetError, ConnectionResetError,
                ConnectionRefusedError) as err:
            print(type(err), ", check address, port, and server status and retry")
            sys.exit()

    def bind(self, client_ip='', client_port=12000):
        self.client.bind((client_ip, client_port))

    def send(self, data):
        """
        :param data: the raw data to serialize
        :return: VOID
        """
        serialized_data = pickle.dumps(data)
        self.client.send(serialized_data)

    def receive(self, max_alloc_buffer=8192):
        """
        :param max_alloc_buffer: Max allowed allocated memory for this data
        :return: the deserialized data.
        """
        data = self.client.recv(max_alloc_buffer)
        deserialized_data = pickle.loads(data)
        if deserialized_data['ack'] == 0:
            print("Successfully connected to {}/{}".format(server_ip, server_port))

        return deserialized_data

    def client_helper(self):
        """
        create a ClientHelper object and initialize it
        """
        helper = ClientHelper(client)
        helper.start()

    def close(self):
        """
        :return: VOID
        """
        self.client.close()


if __name__ == '__main__':
    server_ip = input("Enter server IP address: ")
    server_port = int(input("Enter server port: "))

    # Used for quicker debugging
    # server_ip = "127.0.0.1"
    # server_port = 12000

    client = Client()
    client.connect(server_ip, server_port)  # creates a connection with the server
    client.client_helper()
    client.close()
