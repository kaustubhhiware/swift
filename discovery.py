import os
import pathlib
import pickle
import signal
import socket
import sys
import constants
import utils


self_ip = utils.getNetworkIp()
s = socket.socket()
s.bind((self_ip, constants.DISCOVERY_PORT))

def signal_handler(signal, frame):
	'''
		Close socket before exitting
	'''
	s.close()
	utils.print_log('Stopping discovery server')
	sys.exit(0)


def discovery_server():
	'''
		Run discovery server, and send a list of all IP's previously connected
	'''	
	utils.print_log('Starting discovery server at IP ' + self_ip + ' with pid ' + str(os.getpid()))

	# try:
	# 	s.bind((self_ip, constants.DISCOVERY_PORT))
	# except OSError o:
	# 	print('OSError', o)
	# 	exit(1)
	signal.signal(signal.SIGINT, signal_handler)

	s.listen(20)

	while True:
		sc, address = s.accept()
		utils.print_log('Receieved connection from ' + str(address))

		iplist = []
		if os.path.exists(constants.LOG_FILE):
			with open(constants.LOG_FILE, 'rb') as f:
				iplist = pickle.load(f)

		# remove address if already added in list
		if address in iplist:
			 iplist.remove(address)

		sc.send(pickle.dumps(iplist))

		# save ip in list, and update file
		iplist.append(address[0])
		with open(constants.LOG_FILE, 'wb') as f:
			pickle.dump(iplist, f)

		sc.close()

	s.close()


if __name__ == '__main__':
	utils.print_prompt(discovery=True)
	discovery_server()