import os
import shutil
import sys
import threading

from peerclient.threadedpeerclient import ThreadedPeerClient
from peerserver.threadedpeerserver import ThreadedPeerServer
from utils import constants
from utils.calculation import Calculation
from utils.filehandler import FileHandler
from utils.misc import print_log, print_prompt
from utils.multithreadeddownloader import MultithreadedDownloader
from utils.request import Request


def serve():
    server = None
    filehandle = None

    temp_dir = constants.SERVER_TEMP_DIR
    tracker_host = constants.TRACKER_HOST
    tracker_port = constants.TRACKER_PORT
    tracker_server_address = (tracker_host, tracker_port)
    peer_server_host = ''
    peer_server_port = constants.PEER_SERVER_PORT
    peer_server_address = (peer_server_host, peer_server_port)

    # port used by peer-server to communicate with tracker-server
    bind_port = constants.PEER_SERVER_PORT

    filehandle = FileHandler()
    filehandle.create_dir(temp_dir)
    try:

        server = ThreadedPeerServer(peer_server_address)
        # register the server with tracker
        server.register_with_tracker(tracker_server_address, bind_port)

        proxy = constants.PROXY
        threads = constants.THREADS
        # listen for download requests from client
        server.listen(temp_dir, threads, proxy)

    except Exception as e:
        print("Oops! Error: {}.".format(e)) 

    finally:

        # stop peer server
        if server: 
            server.stop_server()
            # unregister the server with tracker
            server.unregister_with_tracker(tracker_server_address, bind_port)

        # delete the temporary directory
        filehandle.delete_dir(temp_dir)

        # exit
        sys.exit(0)

def request_download(url):
    try:
        tracker_host = constants.TRACKER_HOST
        tracker_port = constants.TRACKER_PORT
        tracker_server_address = (tracker_host, tracker_port)

        temp_dir = constants.CLIENT_TEMP_DIR
        download_dir = constants.CLIENT_DOWNLOAD_DIR
        proxy = constants.PROXY
        threads = constants.THREADS

        try:
            filehandle = FileHandler()
            # make sure that the temp_dir and download_dir exist
            filehandle.create_dir(os.path.abspath(temp_dir))
            filehandle.create_dir(os.path.abspath(download_dir))
        except Exception as e:
            print("Oops! Error: {}.".format(e))

        client = ThreadedPeerClient(url)
        # port used by peer-client to communicate with tracker
        client_tracker_bind_port = constants.CLIENT_SERVER_PORT

        # fetch the list of active servers
        client.fetch_peers_list(tracker_server_address, client_tracker_bind_port)

        # make request to url to get information about file
        req = Request()
        response = req.make_request(url, proxy=proxy)
        req.close_connection(response) 

        # get the filesize
        filesize = int(response.headers['Content-Length'])
        filename = os.path.basename(url.replace("%20", "_"))
        filepath =  download_dir + '/' + filename 

        # if range-download is not supported, use simple download
        if response.headers['Accept-Ranges'] != 'bytes':
            print ("URL doesn't support range download! Using default download...")
            MultithreadedDownloader().download(url, 0, filesize-1, filepath, 
                                            temp_dir, response, threads, proxy)
        # if servers doesn't exist, use simple download
        elif client.num_peer_servers() == 0:
            print ("No peer servers! Using default download...")
            MultithreadedDownloader().download(url, 0, filesize-1, filepath, 
                                            temp_dir, response, threads, proxy)
        else:
            print ("Peer Servers found! Distributing download...")
            print ("peer-client filesize: {}".format(filesize))

            # get the download ranges to be assigned to each
            parts = client.num_peer_servers()
            range_list = Calculation().get_download_ranges_list(0, filesize-1, parts)

            # connect with each server and send them the download details
            client_server_bind_port = constants.CLIENT_SERVER_PORT
            client.connect_with_peer_servers(range_list, temp_dir, client_server_bind_port)

            # wait for download to complete at each server
            # except main_thread, calling join() for each thread
            # it ensures that merging of parts occur only after each thread has -
            # received downloaded part from respective server 
            main_thread = threading.current_thread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
                
            # after receiving all parts, merge them
            with open(filepath,'wb') as wfd:
                for f in range(parts):
                    tempfilepath = temp_dir + "/part" + str(f)
                    with open(tempfilepath, "rb") as fd:
                        shutil.copyfileobj(fd, wfd)     
                    # delete copied segment
                    filehandle.delete_file(tempfilepath)
    except ConnectionError:
        print ("Connection Error! Falling back to download at client...")
    except Exception as e:
        print("Oops! Error: {}.".format(e))
        # delete the file if error occured
        filehandle.delete_file(filepath)
    finally:
        # delete temporary directory
        filehandle.delete_dir(temp_dir)
        # exit
        sys.exit(0)

if __name__ == "__main__":
    print_prompt()
    try:
        newpid = os.fork()
        if newpid != 0:
            serve()
        else:
            while True:
                raw_input = input(">").strip().split()
                if raw_input[0] == "help":
                    print("Available commands are: \n help, request <file_url>")
                elif raw_input[0] == "request":
                    request_download(raw_input[1])
                else:
                    pass
    except Exception as e:
        print_log("Error: %s " % e)
