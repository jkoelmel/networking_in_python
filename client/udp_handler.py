import pickle
import socket


class Tracker:

    def __init__(self, addr, chat=False, user=None, admin=False):
        self.addr = addr[0]
        self.port = int(addr[1])
        self.udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.udpSocket.bind(('', self.port))
        self.chat = chat
        self.user = user
        self.admin = admin
        print(f'UDP client running and accepting other clients at: {addr}')

    def send(self, message, address):
        self.udpSocket.sendto(message, (address[0], int(address[1])))  # address is IP/port tuple
        print(f"Message sent to UDP address: {address}")

    def receive(self):
        while True:
            try:
                data, address = self.udpSocket.recvfrom(1024)
                deserialized_data = pickle.loads(data)
                print("Message: {} received from {}".format(deserialized_data, address))
            except socket.error:
                pass

    def listen(self):
        self.receive()

    def run(self):
        self.listen()
