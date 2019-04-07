"""
Each node starts with broadcasting on a port.
Every node responds back with the requesting IP whose download is going on, if any
"""
import node
import argparse
import logging
import socket
import threading
from node import Node
from message import Message
import messageutils
import sys

NODE_SEND_PORT = 8192
NODE_RECV_PORT = 8193
TIMEOUT = 5

def broadcast_to_peers(ip, neighbors, msg):
	'''

	'''
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('', NODE_SEND_PORT))

	sock.listen(5)
	while True:
		client, address = sock.accept()
		client.settimeout(TIMEOUT)
		threading.Thread(target = sendToPeer,args = (client, address)).start()


def	sendToPeer(self, client, address):
	size = 1024
	while True:
		try:
			# messageutils.make_and_send_message()
			client.send('hey')
			# data = client.recv(size)
			# if data:
			# 	response = data
			# 	client.send(response)
			# else:
			# 	raise error('Client disconnected')
		except:
			client.close()
			return -1


def get_id_from_neighbors(iplist):
	'''
		send self-ip to anyone who's listening
	'''
	tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
	
	hostname = socket.gethostname()
	IPAddr = socket.gethostbyname(hostname)
	tcpServer.bind((IPAddr, NODE_SEND_PORT)) 
	threads = []

	while True: 
		sock.listen(5)
		client, address = sock.accept()
		client.settimeout(60)
		threading.Thread(target = listenToClient,args = (client,address)).start()
		
		
		newthread = ClientThread(ip,port) 
		newthread.run() 
		threads.append(newthread) 
 
	for t in threads: 
		t.join()

def discovery_result(discovery_ip):
	'''
		connect to discoery_ip and populate iplists of neighbors
	'''
	vfile = io.StringIO()
	s = socket.socket()
	s.connect(discovery_ip, 4444)
	d = s.recv(65565)
	print(d)
	while d:
		vfile.write(d)
		d = s.recv(65565)
	s.close()
	vfile.seek(0)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-d','--discovery', action="store", dest="discovery_ip", type=str, help="Specify discovery server IP")
	args = parser.parse_args()

	if args.discovery_ip:
		discovery_ip = args.discovery_ip
	else:
		print('Need to provide discovery IP !')
		exit(0)

	# First contact discovery server tro obtain list of neighbours connected
	iplist = discovery_result(discovery_ip)

	print(iplist)
	exit(0)
	# get an id assigned
	# send all neighbors in iplist a message enquiring their ip and id (if assigned)
	idlist, ip = get_id_from_neighbors(iplist)

	hostname = socket.gethostname()
	IPAddr = socket.gethostbyname(hostname)
	n = Node(IPAddr, ip, [], None, None, idlist)
	
	msg_socket = socket.socket()
	msg_socket.bind(('', NODE_RECV_PORT))
	msg_socket.listen(5)

	while True:
		connection, client_address = msg_socket.accept()
		
		data_list = []
		data = connection.recv(network_params.BUFFER_SIZE)
		while data:
			data_list.append(data)
			data = connection.recv(network_params.BUFFER_SIZE)
		data = b''.join(data_list)

		msg = pickle.loads(data)
		assert isinstance(msg, message.Message), "Received object on socket not of type Message."

		if msg.msg_type == 'HEARTBEAT':
			# do something
			pass
		
		elif msg.msg_type == 'DOWNLOAD_REQUEST':
			# do something
			pass
		elif msg.msg_type == 'ID_REQUEST':
			pass
		