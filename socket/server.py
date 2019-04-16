import sys
from utils import constants
from utils.calculation import Calculation
from utils.filehandler import FileHandler
from peerserver.threadedpeerserver import ThreadedPeerServer

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
