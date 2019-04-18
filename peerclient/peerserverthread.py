"""
Module for Peer Server Thread
"""
import socket
import threading
import json
import os
import time
from utils import constants

class PeerServerThread(threading.Thread):
    ''' establishes and handles the connection to respective peer-server'''

    def __init__(self, url, peer_server_addr, download_range, part_num,
                 temp_dir, client_server_bind_port, attempt_num):
        threading.Thread.__init__(self)
        # port used by thread to communicate with respective peer-server
        self.client_server_bind_port = client_server_bind_port
        self.peer_server_addr = peer_server_addr
        # self.hbeat_port = constants.HEARTBEAT_PORT
        self.url = url
        self.temp_dir = temp_dir
        self.download_range = download_range
        self.part_num = part_num
        self.attempt_num = attempt_num
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.client_server_bind_port))
        # self.hbeat_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.hbeat_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.hbeat_sock.bind(('', self.hbeat_port))

    def run(self):
        """ Runs thread """
        pid = os.fork()
        is_downloaded = False
        # connect to peer-server
        print("[+] Trying to connect to {}".format(self.peer_server_addr))
        self.sock.connect(self.peer_server_addr)
        print("[+] Connected with Server at {}".format(self.peer_server_addr))
        if pid == 0: # Heartbeat thread
            try:
                while not is_downloaded:
                    time.sleep(5)
                    print("[+] Requesting heartbeat from {}".format(self.peer_server_addr))
                    if not self.heartbeat():
                        print("[-] Heartbeat {}".format(self.peer_server_addr))
                else:
                    # In case of failure, exit thread
                    self.close_connection()
            except Exception as e:
                print("Heartbeat thread exception: {}".format(e))
        else: # Download thread
            try:
                # send {"url":"", "range-left":"", "range-right":""} to peer-server
                download_info = {
                    "url": self.url,
                    "range-left": self.download_range[0],
                    "range-right": self.download_range[1]}
                download_info = json.dumps(download_info).encode()
                self.sock.sendall(download_info)
                print("Download info sent: {}".format(download_info))

                filepath = self.temp_dir + 'part{}'.format(str(self.attempt_num) + '_' + str(self.part_num))
                self.receive_file_part(filepath)
                is_downloaded = True
                self.close_connection()
            except Exception as e:
                print("Peer server thread exception: {}".format(e))

    def receive_file_part(self, filepath):
        """ receive file part from server and write at 'filepath' """
        size = 1024
        print("Receiving File part...")
        file = open(filepath, 'wb')
        chunk = self.sock.recv(size)
        while chunk:
            file.write(chunk)
            chunk = self.sock.recv(size)
        file.close()
        print("Done Receiving!")

    def heartbeat(self):
        # TODO: send msg_peek to check for alive connection
        print("Requesting server status from %s" % (self.peer_server_addr))
        size = 1024
        try:
            reply = self.sock.recv(size, socket.MSG_PEEK)
            if reply > 0:
                print("Received heartbeat from %s" % (self.peer_server_addr))
                return True
            else:
                print("Connection Error: could not get heartbeat from %s" % (self.peer_server_addr))
                return False
        except Exception:
            print("Connection Error: could not get heartbeat from %s" % (self.peer_server_addr))
            return False

    def close_connection(self):
        """ Closes connection """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        # self.hbeat_sock.shutdown(socket.SHUT_RDWR)
        # self.hbeat_sock.close()
        print("[-] Peer-Server Disconnected: {}".format(self.peer_server_addr))
