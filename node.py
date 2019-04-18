import os
import shutil
import sys
import threading

from peerclient.threadedpeerclient import ThreadedPeerClient
from peerserver.threadedpeerserver import ThreadedPeerServer
from utils import misc
from utils import request
from utils import constants
from utils import calculation
from utils.multithreadeddownloader import MultithreadedDownloader


def serve():
    server = None

    # creating local copies so that could be passed as args if need be
    temp_dir = constants.SERVER_TEMP_DIR
    discovery_host = constants.DISCOVERY_HOST
    discovery_port = constants.DISCOVERY_PORT
    discovery_server_address = (discovery_host, discovery_port)
    peer_server_host = ''
    peer_server_port = constants.PEER_SERVER_PORT
    peer_server_address = (peer_server_host, peer_server_port)

    misc.create_dir(temp_dir)
    try:
        server = ThreadedPeerServer(peer_server_address)
        server.register_with_discovery(discovery_server_address)

        threads = constants.THREADS
        # listen for download requests from client
        server.listen(threads)

    except Exception as e:
        misc.print_log ("[!] Error in server : {}.".format(e)) 

    finally:
        if server: 
            server.stop_server()
            server.unregister_with_discovery(discovery_server_address)

        misc.delete_dir(temp_dir)
        sys.exit(0)


def request_download(url, firsttime=True, targetLocation=None, missing_range=None, attempt_num=0):
    try:
        discovery_host = constants.DISCOVERY_HOST
        discovery_port = constants.DISCOVERY_PORT
        discovery_server_address = (discovery_host, discovery_port)

        temp_dir = constants.CLIENT_TEMP_DIR
        download_dir = constants.CLIENT_DOWNLOAD_DIR
        threads = constants.THREADS

        try:
            misc.create_dir(os.path.abspath(temp_dir))
            misc.create_dir(os.path.abspath(download_dir))
        except Exception as e:
            misc.print_log ("[!] Error in creating dirs : {}.".format(e))

        client = ThreadedPeerClient(url)
        client.fetch_peers_list(discovery_server_address)

        # make request to url to get information about file
        response = request.make_request(url)
        request.close_connection(response) 
        
        # get the filesize
        if firsttime:
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
            misc.print_log ("[i] Range download not supported! Using default download")
            MultithreadedDownloader().download(url, start, end, filepath, response, threads)
        
        # if servers doesn't exist, use simple download
        elif client.num_peer_servers() == 0:
            misc.print_log ("[i] No peers! Using default download")
            MultithreadedDownloader().download(url, start, end, filepath, response, threads)
        
        # if filesize too small to be distributed, manage alone
        elif filesize <= constants.CHUNK_SIZE:
            misc.print_log ("[i] File size small enough to be downloaded individually")
            MultithreadedDownloader().download(url, start, end, filepath, response, threads)           
        else:
            misc.print_log ("[+] Peer Servers found! Distributing download...")
            misc.print_log ("[+] peer-client filesize: {}".format(filesize))

            # get the download ranges to be assigned to each
            parts = client.num_peer_servers()
            if firsttime:
                range_list = calculation.get_download_ranges_list(0, filesize-1, parts)
            else:
                range_list = calculation.get_download_ranges_list(missing_range[0], missing_range[1], parts)

            misc.print_log ('[d] Assigned download ranges as jobs :')
            for each in zip(range_list, list(client.peer_servers_set)):
                print(each)
            # connect with each server and send them the download details
            client_server_bind_port = constants.CLIENT_SERVER_PORT
            client.connect_with_peer_servers(range_list, attempt_num, filename)

            # wait for download to complete at each server
            # except main_thread, calling join() for each thread
            # it ensures that merging of parts occur only after each thread has -
            # received downloaded part from respective server 
            main_thread = threading.current_thread()
            for t in threading.enumerate():
                if t is main_thread:
                    continue
                t.join()
            
            misc.print_log ('[d] All download threads done')
            # Check which parts have not been downloaded yet, and download them with specific file name
            for part_num in range(parts):
                tempfilepath = temp_dir + filename + '_part' + str(attempt_num) + '_' + str(part_num)
                assigned_range = range_list[part_num]
                actual_file_size = os.stat(tempfilepath).st_size - 1
                expected_file_size = assigned_range[1] - assigned_range[0]

                if os.path.exists(tempfilepath) and expected_file_size == actual_file_size:
                    misc.print_log ('[d] Part num ' + str(part_num) + ' exists of ' +  str(parts))
                    continue
                misc.delete_file(tempfilepath)
                misc.print_log ( '[d][!] Got ' + str(actual_file_size) + ' expected '+ str(expected_file_size) )
                misc.print_log ( '[d][i] Node # {} crashed. Reassigning its downloads'.format(str(part_num)) )
                # recursively call this function, with updated range and attempt number
                request_download(url, firsttime = False,
                                targetLocation = tempfilepath, 
                                missing_range = range_list[part_num], 
                                attempt_num = attempt_num + 1)


            # after receiving all parts, merge them
            with open(filepath,'wb') as wfd:
                for f in range(parts):
                    tempfilepath = temp_dir + filename + "_part" + str(attempt_num) + '_' + str(f)
                    misc.print_log ('[d] Reassembling ' + tempfilepath)
                    with open(tempfilepath, "rb") as fd:
                        shutil.copyfileobj(fd, wfd)     
                    # delete copied segment
                    misc.delete_file(tempfilepath)
            misc.print_log ('[d] Done with the download of ' + filepath)

    except ConnectionError:
        misc.print_log ("[!] Connection Error! Falling back to download at client...")
    except Exception as e:
        misc.print_log ("[!] Download request error: {}.".format(e))
        # delete the file if error occured
        misc.delete_file(filepath)
    finally:
        # delete temporary directory
        # misc.delete_dir(temp_dir)
        # exit
        misc.print_log ('[d] attempt_num ' + str(attempt_num) + ' complete')
        # if attempt_num == 0:
        #     print('k bye')
        #     sys.exit(0)
        return

if __name__ == "__main__":
    misc.print_welcome_prompt()
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
        misc.print_log ("[!] Error: %s " % e)
