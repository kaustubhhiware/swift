import socket
import sys

s = socket.socket()
s.bind(('10.145.88.91', 4444))
s.listen(20)
f = open('discovered.txt','w+')
while True:
	sc, address = s.accept()
	print(address)
	data = f.readlines()
	for line in data:
		if line == address:
			data.remove(line)
	b = bytes('\n'.join(data), 'utf-8')
	print(b)
	f.seek(0)
	x  =f.read()
	while f:
		s.send(bytes(x, 'utf-8'))
		x = f.read()

	data.append(address[0])
	f.writelines('\n'.join(data))
	sc.close()
s.close()
f.close()

# import socket
# import io
#
# vfile = io.StringIO()
# s = socket.socket()
# s.connect('discoveryip', 4444)
# d = s.recv(65565)
# print(d)
# while d:
# 	vfile.write(d)
# 	d = s.recv(65565)
# s.close()
# vfile.seek(0)
#
# # data = vfile.read
# #data should be a list of strings of addresses