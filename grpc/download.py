'''
 https://doc-0c-68-docs.googleusercontent.com/docs/securesc/am1ueff1eolsmtoh96qjjicnui5q64lf/7907qj1ntn1sp6qrmmg52ivt448bth5u/1554890400000/13601236613844276836/00316766863666355120/1gTrLTODppre0ovYuXCWC_fzRRAcV75i9?e=download&nonce=o8p10k0p30qa0&user=00316766863666355120&hash=f1r3afqmmk89a79fu7hm23et315s15e9
ftp://ftp.se.debian.org/cdimage/archive/3.0_r6/i386/iso-dvd/debian-30r6-dvd-i386-binary-1.iso
NO login: 
ftp://ftp.se.debian.org/cdimage/archive/3.0_r6/i386/iso-dvd/MD5SUMS
http://cse.iitkgp.ac.in/~hknarendra/CaseDocuments.zip
http://cse.iitkgp.ac.in/~hknarendra/video.mp4
'''

'''
 curl 'http://saimei.ftp.acc.umu.se/cdimage/archive/3.0_r6/i386/iso-dvd/debian-30r6-dvd-i386-binary-1.iso' -H 'Proxy-Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Mobile Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: http://ftp.acc.umu.se/cdimage/archive/3.0_r6/i386/iso-dvd/' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7' --compressed
'''
'''
 curl 'http://cse.iitkgp.ac.in/~hknarendra/CaseDocuments.zip' -H 'Proxy-Connection: keep-alive' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Mobile Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: http://ftp.acc.umu.se/cdimage/archive/3.0_r6/i386/iso-dvd/' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7' --compressed -r 100000000-200000000 --output x
'''
import os

def get_file_size_curl(url):
	'''
		use curl to get file size
	'''
	file_size_command = 'curl "' + url + '" -H "Proxy-Connection:keep-alive" -sI'
	size_command_exec = os.popen(file_size_command).read().split('\n')

	# file not found
	if size_command_exec[0].endswith('404 Not Found'):
		return -1

	for line in size_command_exec:
		if not line.startswith('Content-Length'):
			continue

		length = int(line.split(':')[-1])
		return length

	return -1
	# -1 means could not retrieve / file not found


def download_file_curl(url, start, end, save_location):
	'''
		Function to download partial content via curl.
		This function cannot be stopped in the middle.
	'''
	file_size = get_file_size_curl(url)

	if file_size == -1:
		return False # 'Could not retrieve file / file not found'

	file_name = url.split('/')[-1]
	out_file = save_location + '/' + str(start) + '-' +str(end) + '-' + file_name
	download_command = 'curl "' + url+ '" -H "Proxy-Connection: keep-alive" --compressed -r '
	download_command += str(start) + '-' + str(end) + ' --output ' + out_file + ' --progress-bar'

	download_command_exec = os.popen(download_command).read().split('\n')
	return True


def get_file_size_local(file):
	'''
		get local file size. Useful for heartbeat.
	'''
	if not os.path.exists(file):
		return -1

	statinfo = os.stat(file)
	return statinfo.st_size

def get_file_name(url):
	return url.split('/')[-1]