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
from utils.request import Request
from utils.multithreadeddownloader import MultithreadedDownloader
from utils.calculation import Calculation
from utils.filehandler import FileHandler


class PeerClientThread(threading.Thread):
    """ class for a thread which handles a peer-client connection"""
    def __init__(self, client_conn, client_addr, temp_dir, threads, proxy):
        threading.Thread.__init__(self)
        self.client_conn = client_conn
        # self.hbeat_client_conn = hbeat_client_conn
        self.client_addr = client_addr
        # self.hbeat_client_addr = hbeat_client_addr
        self.temp_dir = temp_dir
        self.threads = threads
        self.proxy = proxy

    def run(self):
        size = 1024
        # receive {"url":"", "range-left":"", "range-right":""} from client
        msg = self.client_conn.recv(size)
        if msg:
            msg = msg.decode()
            print("[+] Received Message: {}".format(msg))
            msg = json.loads(msg)

            # generate a random name for file
            filename = Calculation().generate_random_string(12)
            filepath = self.temp_dir + filename

            # use request to download
            url = msg['url']
            range_left = msg['range-left']
            range_right = msg['range-right']
            response = Request().make_request(url, self.proxy)

            # use Multiprocess to download using multithreading
            print("starting new process to download {}".format(filename))
            process = multiprocessing.Process(
                target=MultithreadedDownloader().download,
                args=(
                    url,
                    range_left,
                    range_right,
                    filepath,
                    self.temp_dir,
                    response,
                    self.threads,
                    self.proxy,
                )
            )

            pid = os.fork()
            download_complete = False
            if pid == 0: # Heartbeat thread
                while not download_complete:
                    time.sleep(5)
                    print("[+] Requesting heartbeat from {}".format(self.client_addr))
                    if self.heartbeat():
                        print("[-] Heartbeat {}".format(self.client_addr))
                    else:
                        print("[-] Heartbeat failed. Stopping download since client is disconnected.")
                        process.terminate()
            else: # Download thread
                process.start()
                download_complete = True
            process.join()
            print('Out of process for file {}'.format(filename))

            # send the downloaded file part to peer-client
            self.send_file_part(filepath)

            # let peer-client know that file sending is done
            self.client_conn.shutdown(socket.SHUT_RDWR)

            # close connection with peer-client
            self.client_conn.close()
            print("[-] Client Disconnected: {}".format(self.client_addr))

            # delete temp file
            FileHandler().delete_file(filepath)
            print("[-] Temp File Deleted.")

    def send_file_part(self, filepath):
        """ function for sending file at 'filepath' through socket to client """
        file = open(filepath, 'rb')
        chunk = file.read(1024)
        print('Sending...')
        try:
            while chunk:
                self.client_conn.send(chunk)
                chunk = file.read(1024)
            file.close()
            print("Done Sending File!")
        except IOError as e:
            print("Client disconnected, Got IOError: {}. Stopping download".format(e))

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