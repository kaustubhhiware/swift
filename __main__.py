"""
Each node starts with broadcasting on a port.
Every node responds back with the requesting IP whose download is going on, if any
"""
import argparse
import asyncio
import pickle
import socket
import sys
import threading
import constants
import utils
from node import Node
from message import Message

# shift to constants later
NODE_SEND_PORT = 8192
NODE_RECV_PORT = 8193
TIMEOUT = 5
BUFFER_SIZE = 1048576
DISCOVERY_PORT = 4444

# async send_to_peer(msg,  )


# shift function to utils later - maybe
def broadcast_to_peers(msg_type, content, peers):
	'''
		Returns dictionary of responses to all neighbors
	'''
	if msg_type == 'ID_REQUEST':
		peer_ids = {}

	for peer in peers:
		# TODO: do some threading stuff
		if msg_type == 'ID_REQUEST':
			# peer_id = await send_to_peer()
			peer_id = 2
			peer_ids[peer] = peer_id


	if msg_type == 'ID_REQUEST':
		return peer_ids
	# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# sock.bind(('', NODE_SEND_PORT))
	# sock.listen(5)

	# # if msg_type == 'ID_REQUEST':
	# while True:
	# 	client, address = sock.accept()
	# 	client.settimeout(TIMEOUT)
	# 	threading.Thread(target = sendToPeer,args = (client, address)).start()


def get_id_from_neighbors(self_ip, neighbors):
	'''
		broadcast self ip to all neighbors, asking for their id
	'''
	# msg = Message(msg_type='ID_REQUEST', content={ip: self_ip}, file_path=None, file=None)
	responses = broadcast_to_peers(msg_type='ID_REQUEST', content={ip: self_ip}, peers=neighbors)

	# returns dictionary of IP: id
	return response_dict


def discover_nodes(discovery_ip):
	'''
		connect to discoery_ip and populate iplists of neighbors
	'''
	s = socket.socket()
	s.connect((discovery_ip, DISCOVERY_PORT))

	iplist = pickle.loads(s.recv(BUFFER_SIZE))
	return iplist


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--discovery', action="store", dest="discovery_ip", type=str, help="Specify discovery server IP")
	args = parser.parse_args()

	utils.print_prompt()

	if args.discovery_ip:
		discovery_ip = args.discovery_ip
	else:
		print('Need to provide discovery server IP !')
		exit(0)

	self_ip = utils.getNetworkIp()
	utils.print_log('Starting connection from ' + self_ip)

	# First contact discovery server tro obtain list of neighbours connected
	iplist = discover_nodes(discovery_ip)
	id_ = len(iplist) + 1

	iplist = list(set(iplist))
	utils.print_log('Received neighbors ' +str(iplist))
	exit(0)

	# get an id assigned
	# send all neighbors in iplist a message enquiring their id
	# active_neighbors = get_id_from_neighbors(self_ip=self_ip, neighbors=iplist)

	# idlist = active_neighbors.keys()
	# assign id
	# id_ = 1
	# if idlist is not None:
	# 	id_ = max(active_neighbors.values()) + 1

	node = Node(ip=self_ip, id=id_, requesting_id=[],
			requesting_file=None, dl_queue=None, neighbors=iplist)
	

	msg_socket = socket.socket()
	msg_socket.bind(('', NODE_RECV_PORT))
	msg_socket.listen(5)

	
	while True:
		connection, client_address = msg_socket.accept()
		
		data_list = []
		data = connection.recv(BUFFER_SIZE)
		while data:
			data_list.append(data)
			data = connection.recv(BUFFER_SIZE)
		data = b''.join(data_list)

		msg = pickle.loads(data)
		assert isinstance(msg, message.Message), "Received object on socket not of type Message."

		# LOT NEEDS TO BE WRITTEN HERE
		# when this node is collaborator
		if msg.msg_type == 'HEARTBEAT' and node.ip != node.requesting_id[0]:
			# do something
			pass
		
		# collaborator / manager agnostic
		elif msg.msg_type == 'DOWNLOAD_REQUEST':
			# handle case if requested file is same as currently downloading file
			# do something
			pass

		# collaborator / manager agnostic
		elif msg.msg_type == 'ID_REQUEST':

			pass

		elif msg.msg_type == 'PAUSE_NEW':
			# new node joined, pause all downloads
			# this can be sent only by the temp server
			pass
		# when this node is temporary server
		# send back HEARTBEAT

		