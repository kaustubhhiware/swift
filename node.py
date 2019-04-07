class Node(object):
	'''
		Corresponding to each node, we have
		- an id: Assigned sequentially
		- a requesting ip whose download is ongoing
		- requested_file - file to be downloaded
		- file_start, file_end - fragments assigned to download
		- a download queue list : Empty at init
		- neighbors: a list of nodes in the network
		- For now, we assume the directory made available for sharing is the current directory
	'''

	def __init__(self, ip, id=-1, requesting_id=[], requesting_file=None, dl_queue=None, neighbors = []):
		self.ip = ip
		self.id = id
		self.requesting_id = []
		self.requesting_file = requesting_file
		self.dl_queue = dl_queue
		self.file_start, self.file_end = None, None
		self.sharing = '.'
		self.neighbors = []

	def set_id(id_list):
		'''
			Given a list of ids, assign its own id as max id in list + 1
		'''
		if id_list is None:
			id_list = [0]
		self.id = max(id_list) + 1

	def set_requesting(idx, file):
		self.requesting_id = idx
		self.requesting_file = file

	def set_request_file_bounds(start, end):
		self.file_start = start
		self.file_end = end