"""
    Thread to control connection from peers
"""
import socket
from discovery.nettracker import NetTracker
from discovery.peerthread import PeerThread
from utils import misc

class ThreadedDiscoveryServer:
    """
        Handling threaded connection from peers
    """
    def __init__(self, discovery_server_address):
        self.discovery_server_address = discovery_server_address
        self.discovery = NetTracker()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.discovery_server_address)

    def listen(self):
        """
            listens for client connections
        """
        self.sock.listen(5)
        misc.print_log ("[i] Listening for clients...")
        while True:
            peer_conn, peer_addr = self.sock.accept()
            misc.print_log ("[+] Peer Connected: {}".format(peer_addr))
            #client.settimeout(60)
            new_peer_thread = PeerThread(self.discovery, peer_conn, peer_addr)
            #new_peer_thread.daemon = True
            new_peer_thread.start()

    def stop_server(self):
        """ stop discovery server execution """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        misc.print_log ("[-] Stopped Tracker Server.")
