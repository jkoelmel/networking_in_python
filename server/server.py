import socket
from threading import Thread

from client_handler import ClientHandler


class Server(object):
    """
    The server class implements a server socket that can handle multiple client connections.
    It is really important to handle any exceptions that may occur because other clients
    are using the server too, and they may be unaware of the exceptions occurring. So, the
    server must not be stopped when a exception occurs. A proper message needs to be show in the
    server console.
    """
    MAX_NUM_CONN = 10  # keeps 10 clients in queue

    def __init__(self, host="localhost", port=12000):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # your implementation for this socket here
        self.handlers = {}  # initializes client_handlers list

    def _bind(self):
        """
        :return: VOID
        """
        self.server.bind((self.host, self.port))

    def _listen(self):
        """
        :return: VOID
        """
        try:
            self._bind()
            self.server.listen(Server.MAX_NUM_CONN)
            print("Server is running without issues")
            print("Server listening at {}/{}".format(self.host, self.port))
        except (ConnectionError, ConnectionAbortedError, ConnectionRefusedError, OSError) as err:
            print(type(err), err)

    def _accept_clients(self):
        """
        :return: VOID
        """
        while True:
            clientsocket, addr = self.server.accept()
            Thread(target=self._handler, args=(clientsocket, addr)).start()  # start client thread

    def _handler(self, clientsocket, addr):
        """
        :clienthandler: the clienthandler child process that the server creates when a client is accepted
        :addr: the addr list of server parameters created by the server when a client is accepted.
        """
        clienthandler = ClientHandler(self, clientsocket, addr)
        self.handlers[addr] = clienthandler  # Set clientID as key, and socket object as value
        clienthandler.run()

    def run(self):
        """
        Run the server.
        :return: VOID
        """
        self._listen()
        self._accept_clients()


if __name__ == '__main__':
    server = Server()
    server.run()
