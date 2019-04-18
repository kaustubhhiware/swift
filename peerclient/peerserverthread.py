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
        # self.hbeat_port = constants.HEARTBEAT_PORT
        # self.hbeat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.hbeat_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.hbeat_sock.bind(('', self.hbeat_port))

    def run(self):
        """
            Runs thread
        """
        pid = os.fork()
        is_downloaded = False
        if pid == 0: 
            # Heartbeat thread
            pass
            # try:
            #     print("[+] Trying to connect to {}".format(self.peer_server_addr))
            #     self.hbeat_sock.connect(self.peer_server_addr)
            #     print("[+] Connected with Server at {}".format(self.peer_server_addr))
            #     num_failures = 0
            #     # Can tolerate upto 2 consecutive heartbeat failures
            #     while num_failures < 2 and not is_downloaded:
            #         time.sleep(5)
            #         print("[+] Requesting heartbeat from {}".format(self.peer_server_addr))
            #         if not self.heartbeat():
            #             print("[-] Heartbeat {}".format(self.peer_server_addr))
            #             num_failures += 1
            #         else:
            #             num_failures = 0
            #     else:
            #         # In case of failure, exit thread
            #         self.close_connection()
            # except Exception as e:
            #     print("Heartbeat thread exception: {}".format(e))
        else: # Download thread
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
                is_downloaded = True
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

    # def heartbeat(self):
    #     # hbeat_request = "hbeat"
    #     # print("Requesting server status from %s" % (self.peer_server_addr))
    #     # self.hbeat_sock.send(hbeat_request)
    #     size = 1024
    #     try:
    #         reply = self.hbeat_sock.recv(size)
    #         if reply == "ack":
    #             return True
    #     except Exception:
    #         return False

    def close_connection(self):
        """ Closes connection """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        # self.hbeat_sock.shutdown(socket.SHUT_RDWR)
        # self.hbeat_sock.close()
        misc.print_log ("[-] Peer-Server Disconnected: {}".format(self.peer_server_addr))
