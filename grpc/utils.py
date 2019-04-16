import socket
import time
import constants

def print_prompt(discovery=False):
	file = 'prompt_discovery' if discovery else 'prompt' 
	with open(file, 'r') as f:
		txt = f.readlines()
	txt = ''.join(txt)
	print(txt)


def getNetworkIp():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.connect(('<broadcast>', 0))
	return s.getsockname()[0]


def print_log(message):
	print(time.strftime('[%d %b %Y - %H:%M:%S] ') + message)