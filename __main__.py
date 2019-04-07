"""
Each node starts with broadcasting on a port.
Every node responds back with the requesting IP whose download is going on, if any
"""

import node
import grpcio

NODE_SEND_PORT = 8192
NODE_RECV_PORT = 8193
JOIN_TIMEOUT = 30 # seconds

def beacon():
	'''
		send self-ip to anyone who's listening
	'''
	self_ip = socket.gethostbyname(socket.gethostname()) 
	sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sckt.settimeout(2)
	sckt.bind(('', NODE_SEND_PORT))
	sckt.listen(5)

	broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	while True:
		broadcastSocket.sendto(socket.gethostbyname(socket.getfqdn()) + ' ' + str(NODE_SEND_PORT), ('<broadcast>', NODE_RECV_PORT))
		try:
			sock, address = sckt.accept()
			break
		except socket.timeout:
			pass
	broadcastSocket.close()
	sock.settimeout(JOIN_TIMEOUT)


if __name__ == '__main__':
	# First send a beacon signalling requesting IP
	beacon()