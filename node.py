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

def request_download(url, firsttime=True, targetLocation=None, missing_range=None, attempt_num=0):
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
        if firsttime:

            # get the filesize
            filesize = int(response.headers['Content-Length'])
        else:
            filesize = missing_range[1] - missing_range[0] + 1

        filename = os.path.basename(url.replace("%20", "_"))
        if not firsttime and targetLocation is not None:
            filepath = targetLocation
        else:
            filepath =  download_dir + filename

        if firsttime:
            start, end = 0, filesize-1
        else:
            start, end = missing_range
        # if range-download is not supported, use simple download
        if response.headers['Accept-Ranges'] != 'bytes':
            print ("URL doesn't support range download! Using default download...")
            MultithreadedDownloader().download(url, start, end, filepath, 
                                            temp_dir, response, threads, proxy)
        # if servers doesn't exist, use simple download
        elif client.num_peer_servers() == 0:
            print ("No peer servers! Using default download...")
            MultithreadedDownloader().download(url, start, end, filepath, 
                                            temp_dir, response, threads, proxy)
        elif filesize <= constants.CHUNK_SIZE:
            print ("File size small enough to be downloaded individually...")
            MultithreadedDownloader().download(url, start, end, filepath, 
                                            temp_dir, response, threads, proxy)            
        else:
            print ("Peer Servers found! Distributing download...")
            print ("peer-client filesize: {}".format(filesize))

            # get the download ranges to be assigned to each
            parts = client.num_peer_servers()
            if firsttime:
                range_list = Calculation().get_download_ranges_list(0, filesize-1, parts)
            else:
                range_list = Calculation().get_download_ranges_list(missing_range[0], missing_range[1], parts)

            print('Jobs')
            for each in zip(range_list, list(client.peer_servers_set)):
                print(each)
            # connect with each server and send them the download details
            client_server_bind_port = constants.CLIENT_SERVER_PORT
            client.connect_with_peer_servers(range_list, temp_dir, client_server_bind_port, attempt_num)

            # wait for download to complete at each server
            # except main_thread, calling join() for each thread
            # it ensures that merging of parts occur only after each thread has -
            # received downloaded part from respective server 
            main_thread = threading.current_thread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
            
            print('All threads done')
            # Check which parts have not been downloaded yet, and download them with specific file name
            for part_num in range(parts):
                tempfilepath = temp_dir + 'part' + str(attempt_num) + '_' + str(part_num)
                assigned_range = range_list[part_num]
                actual_file_size = os.stat(tempfilepath).st_size - 1
                expected_file_size = assigned_range[1] - assigned_range[0]

                if os.path.exists(tempfilepath) and expected_file_size == actual_file_size:
                    print('Part num', str(part_num), 'exists of ', parts)
                    continue
                if os.path.exists(tempfilepath):
                    filehandle.delete_file(tempfilepath)
                print('Got ', str(actual_file_size), ' expected ',expected_file_size)
                print ('[+] Node # {} crashed. Reassigning its downloads'.format(str(part_num)))
                request_download(url, firsttime = False,
                                targetLocation = tempfilepath, 
                                missing_range = range_list[part_num], 
                                attempt_num = attempt_num + 1)


            # after receiving all parts, merge them
            with open(filepath,'wb') as wfd:
                for f in range(parts):
                    tempfilepath = temp_dir + "part" + str(attempt_num) + '_' + str(f)
                    print('Reassembling ', tempfilepath)
                    with open(tempfilepath, "rb") as fd:
                        shutil.copyfileobj(fd, wfd)     
                    # delete copied segment
                    filehandle.delete_file(tempfilepath)
            print('Done with the download of ',filepath)

    except ConnectionError:
        print ("Connection Error! Falling back to download at client...")
    except Exception as e:
        print("Download request error: {}.".format(e))
        # delete the file if error occured
        filehandle.delete_file(filepath)
    finally:
        # delete temporary directory
        # filehandle.delete_dir(temp_dir)
        # exit
        print('attempt_num', attempt_num, 'complete')
        # if attempt_num == 0:
        #     print('k bye')
        #     sys.exit(0)
        return

if __name__ == "__main__":
    print_prompt()
    try:
        newpid = os.fork()
        if newpid != 0:
            serve()
            # pass
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
