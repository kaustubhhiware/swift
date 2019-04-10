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

	def __init__(self, ip, id_=-1, requesting_id=[], requesting_file=None, dl_queue=None, neighbors = []):
		self.ip = ip
		self.id = id_
		self.requesting_id = []
		self.requesting_file = requesting_file
		self.dl_queue = dl_queue # redundant
		self.file_start, self.file_end = None, None 
		self.sharing = '.'
		self.neighbors = []

	def set_requesting(idx_list, file):
		self.requesting_id = idx_list
		self.requesting_file = file

	def set_request_file_bounds(start, end):
		self.file_start = start
		self.file_end = end