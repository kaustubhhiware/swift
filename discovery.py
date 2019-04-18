import sys
import threading
from utils import constants
from utils import misc
from discovery.threadeddiscoveryserver import ThreadedDiscoveryServer

if __name__ == "__main__":
    misc.print_welcome_prompt(discovery=True)
    server = None
    try:
        discovery_host = ''
        discovery_port = constants.DISCOVERY_PORT
        discovery_server_address = (discovery_host, discovery_port)
        server = ThreadedDiscoveryServer(discovery_server_address)
        server.listen()
    
    except Exception as err:
        misc.print_log ("[!] Oops! Error in discovery : {}.".format(err))

    finally:
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.close_connection()
        if server:
            server.stop_server()
    