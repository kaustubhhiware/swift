import socket
from utils import constants
from utils import misc
from peerserver.peerclientthread import PeerClientThread


class ThreadedPeerServer:
    """
        Multithreaded peer-server that assigns single thread to each peer-client connection
    """
    def __init__(self, server_address):
        self.server_address = server_address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_address)

    def register_with_discovery(self, discovery_server_address):
        """
            connect to discovery and register ip
        """
        misc.print_log ("[i] Discovery server address: " + str(discovery_server_address) )
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('', constants.PEER_SERVER_PORT))
        connection.connect(discovery_server_address)
        misc.print_log ("[+] Connected with Discovery server.")
        
        # register the peer-server
        connection.send("addme".encode())
        misc.print_log ("[+] Sent addme request.")
        # close the connection to discovery
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        misc.print_log ("[-] Disconnected with Discovery server.")

    def listen(self, threads):
        self.sock.listen(5)
        misc.print_log ("[i] Listening for clients...")
        while True:
            client_conn, client_addr = self.sock.accept()
            misc.print_log ("[+] Client Connected: {}".format(client_addr))
            # client.settimeout(60)
            # assigning a thread to each client connected
            new_client_thread = PeerClientThread(
                client_conn,
                client_addr,
                threads
            )
            new_client_thread.start()

    def unregister_with_discovery(self, discovery_server_address):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('', constants.PEER_SERVER_PORT))
        connection.connect(discovery_server_address)
        misc.print_log("[i] Connected with Discovery server.")
        
        # unregister the peer-server
        connection.send("removeme".encode())
        misc.print_log ("[-] Sent removeme request.")
        # close the connection to discovery
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        misc.print_log ("[-] Disconnected with Discovery server.")

    def stop_server(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        misc.print_log ("[-] Stopped Peer Server.")
