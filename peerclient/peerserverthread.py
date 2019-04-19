import socket
import threading
import json
import os
import time
from utils import constants
from utils import misc

class PeerServerThread(threading.Thread):
    '''
        establishes and handles the connection to respective peer-server
    '''

    def __init__(self, url, peer_server_addr, download_range, part_num,
                 attempt_num, filename):
        threading.Thread.__init__(self)
        # port used by thread to communicate with respective peer-server
        self.peer_server_addr = peer_server_addr
        self.url = url
        self.download_range = download_range
        self.part_num = part_num
        self.attempt_num = attempt_num
        self.filename = filename
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', constants.CLIENT_SERVER_PORT))

    def run(self):
        """
            Runs thread
        """
        try:
            # connect to peer-server
            misc.print_log ("[+] Trying to connect to {}".format(self.peer_server_addr))
            self.sock.connect(self.peer_server_addr)
            misc.print_log ("[+] Connected with Server at {}".format(self.peer_server_addr))

            download_info = {
                "url": self.url,
                "range-left": self.download_range[0],
                "range-right": self.download_range[1]}
            download_info = json.dumps(download_info).encode()
            self.sock.sendall(download_info)
            misc.print_log ("[i] Download info sent: {}".format(download_info))

            filepath = constants.CLIENT_TEMP_DIR + self.filename + '_part{}'.format(str(self.attempt_num) + '_' + str(self.part_num))
            self.receive_file_part(filepath)
            self.close_connection()
        except Exception as e:
            misc.print_log ("[!] Peer server thread exception: {}".format(e))

    def receive_file_part(self, filepath):
        """ receive file part from server and write at 'filepath' """
        size = 1024
        misc.print_log ("[i] Receiving File part...")
        file = open(filepath, 'wb')
        chunk = self.sock.recv(size)
        while chunk:
            file.write(chunk)
            chunk = self.sock.recv(size)
        file.close()
        misc.print_log ("[i] Done Receiving!")

    def close_connection(self):
        """ Closes connection """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        # self.hbeat_sock.shutdown(socket.SHUT_RDWR)
        # self.hbeat_sock.close()
        misc.print_log ("[-] Peer-Server Disconnected: {}".format(self.peer_server_addr))
