import sys
import threading
from utils import constants
from utils.misc import print_prompt
from trackermodule.threadedtrackerserver import ThreadedTrackerServer

if __name__ == "__main__":
    print_prompt(discovery=True)
    server = None
    try:
        tracker_host = ''
        tracker_port = constants.TRACKER_PORT
        tracker_server_address = (tracker_host, tracker_port)
        server = ThreadedTrackerServer(tracker_server_address)
        server.listen()
    
    except Exception as err:
        print("Oops! Error: {}.".format(err))

    finally:
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.close_connection()
        if server:
            server.stop_server()
    