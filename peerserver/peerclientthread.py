"""
Manages threads that handle connection with clients
"""
import threading
import socket
import multiprocessing
import json
import os
import time
from utils import constants
from utils import request
from utils import calculation
from utils import misc
from utils.multithreadeddownloader import MultithreadedDownloader


class PeerClientThread(threading.Thread):
    """ class for a thread which handles a peer-client connection"""
    def __init__(self, client_conn, client_addr, threads):
        threading.Thread.__init__(self)
        self.client_conn = client_conn
        # self.hbeat_client_conn = hbeat_client_conn
        self.client_addr = client_addr
        # self.hbeat_client_addr = hbeat_client_addr
        self.threads = threads

    def run(self):
        pid = os.fork()
        if pid == 0: # Heartbeat thread
            pass
            # size = 1024
            # msg = self.hbeat_client_conn.recv(size)
            # if msg == "hbeat":
                # print("[+] Received Heartbeat from {}: {}".format(self.client_addr, msg))
            # while True:
            #     self.hbeat_client_conn.send("ack")
            #     time.sleep(5)
            #     print("[+] Sent heartbeat to {}: {}".format(self.client_addr, msg))
        else:
            size = 1024
            # receive {"url":"", "range-left":"", "range-right":""} from client
            msg = self.client_conn.recv(size)
            if msg:
                msg = msg.decode()
                misc.print_log ("[+] Received Message: {}".format(msg))
                msg = json.loads(msg)

                # generate a random name for file
                filename = calculation.generate_random_string(12)
                filepath = constants.SERVER_TEMP_DIR + filename

                # use request to download
                url = msg['url']
                range_left = msg['range-left']
                range_right = msg['range-right']
                response = request.make_request(url)

                # use Multiprocess to download using multithreading
                misc.print_log ("[i] Starting new process to download {}".format(filename))
                process = multiprocessing.Process(
                    target=MultithreadedDownloader().download,
                    args=(
                        url,
                        range_left,
                        range_right,
                        filepath,
                        response,
                        self.threads,
                    )
                )
                process.start()
                process.join()
                misc.print_log ('[i] Out of process for file {}'.format(filename))

                self.send_file_part(filepath)
                self.client_conn.shutdown(socket.SHUT_RDWR)
                self.client_conn.close()
                misc.print_log ("[-] Client Disconnected: {}".format(self.client_addr))

                misc.delete_file(filepath)
                misc.print_log ("[-] Temp File Deleted.")

    def send_file_part(self, filepath):
        """
            function for sending file at 'filepath' through socket to client
        """
        file = open(filepath, 'rb')
        chunk = file.read(1024)
        misc.print_log ('[i] Sending...')
        try:
            while chunk:
                self.client_conn.send(chunk)
                chunk = file.read(1024)
            file.close()
            misc.print_log ("[i] Done Sending File!")
        except IOError as e:
            misc.print_log ("[!] Client disconnected, Got IOError: {}. Stopping download".format(e))

    def heartbeat(self):
        print("Requesting server status from %s" % (self.client_addr))
        size = 1024
        try:
            reply = self.client_conn.recv(size, socket.MSG_PEEK)
            if reply > 0:
                print("Received heartbeat from %s" % (self.client_addr))
                return True
            else:
                print("Connection Error: could not get heartbeat from %s" % (self.client_addr))
                return False
        except Exception:
            print("Connection Error: could not get heartbeat from %s" % (self.client_addr))
            return False
