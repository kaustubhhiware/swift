from utils import misc

class NetTracker:
    def __init__(self):
        self.peer_servers_set = set()

    def add_peer(self, peer_server):
        self.peer_servers_set.add(peer_server)

    def remove_peer(self, peer_server):
        try:
            self.peer_servers_set.remove(peer_server)
        except KeyError:
            misc.print_log ("[i] {} is not in the list of connected peers!".format(peer_server))

    def get_peer_servers_list(self):
        return self.peer_servers_set
