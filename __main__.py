"""
Each node starts with broadcasting on a port.
Every node responds back with the requesting IP whose download is going on, if any
"""
import node
import grpcio
import argparse
import logging
import socket
from node import Node

NODE_SEND_PORT = 8192
NODE_RECV_PORT = 8193
TIMEOUT = 5

def broadcast_to_peers(ip, neighbors, msg):
	'''

	'''
	s = socket.socket()
	s.bind(('0.0.0.0', NODE_SEND_PORT))

	for neighbor in neighbors:
		s.listen(TIMEOUT)
		while True:
			c, addr = s.accept()
			print 'Got connection from', addr
			print c.recv(1024)
			c.close()



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
		tcpServer.listen(4) 
		print "Multithreaded Python server : Waiting for connections from TCP clients..." 
		(conn, (ip,port)) = tcpServer.accept() 
		
		
		newthread = ClientThread(ip,port) 
		newthread.run() 
		threads.append(newthread) 
 
	for t in threads: 
		t.join()


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
	iplist = discovery_result(args.discovery_ip)

	# get an id assigned
	# send all neighbors in iplist a message enquiring their ip and id (if assigned)
	idlists, iplist = get_id_from_neighbors(iplist)

