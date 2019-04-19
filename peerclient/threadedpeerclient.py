import ast
import socket
from peerclient.peerserverthread import PeerServerThread
from utils import constants
from utils import misc

def eval_code(code):
    parsed = ast.parse(code, mode='eval')
    fixed = ast.fix_missing_locations(parsed)
    compiled = compile(fixed, '<string>', 'eval')
    return eval(compiled)


class ThreadedPeerClient:
    """
        handles connections with servers
    """
    def __init__(self, url):
        self.url = url
        self.peer_servers_set = None

    def fetch_peers_list(self, discovery_server_address):
        """
            Fetches list of peer servers
        """
        # connect to discovery
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('', constants.CLIENT_SERVER_PORT))
        connection.connect(discovery_server_address)
        misc.print_log ("[+] Connected with Discovery server.")

        connection.send("sendpeerslist".encode())
        misc.print_log ("[+] Sent sendpeerslist request.")
        # receive peers list as a set of address tuples
        msg = connection.recv(1024)
        msg = msg.decode()
        misc.print_log (msg)
        misc.print_log (eval_code(msg))
        if msg == "None":
            self.peer_servers_set = set()
        else:
            self.peer_servers_set = eval_code(msg)
        misc.print_log ("[+] Received Peers List: {}".format(self.peer_servers_set))
        # close the connection to discovery
        connection.shutdown(socket.SHUT_RDWR)
        connection.close()
        misc.print_log ("[-] Disconnected with Discovery server.")

    def num_peer_servers(self):
        return len(self.peer_servers_set)

    def connect_with_peer_servers(self, range_list, attempt_num, filename):
        """
            create connection with peer servers
        """
        misc.print_log ("[i] Trying to connect to peer servers...")
        part_num = 0
        for peer_server_addr in self.peer_servers_set:
            download_range = range_list[part_num]
            new_server_thread = PeerServerThread(
                self.url,
                peer_server_addr,
                download_range,
                part_num,
                attempt_num, 
                filename
            )
            part_num += 1
            new_server_thread.start()
