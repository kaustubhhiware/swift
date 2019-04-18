"""
Performs Multithreaded download
"""
import urllib3
import logging
import os
import sys
import shutil
import threading
import pathlib
from utils import misc
from utils import request
from utils import constants
from utils import calculation


class MultithreadedDownloader:
    """
        Main class providing interface for download
    """
    def __init__(self):
        self.url = None 
        self.range_left = None
        self.range_right = None
        self.threads = None 
        self.filepath = None 
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def range_download_support(self, resp):
        """
            returns boolean value indicating support for range downloading
        """
        try:
            supported = (resp.headers['Accept-Ranges'] == 'bytes')
        except KeyError:
            supported = False

        return supported

    def multithreaded_download(self, ranges_list):
        """
            function to perform multithreaded download
        """
        # downloading each segment
        for f in range(self.threads):
            # calling download_range() for each thread
            t = threading.Thread(target=request.download_range,
                kwargs={
                'url': self.url,
                'filepath': constants.SERVER_TEMP_DIR + "/temp" + str(f), 
                'range_left': ranges_list[f][0],
                'range_right': ranges_list[f][1],
                })
            t.setDaemon(True)
            t.start()   

        # except main_thread, calling join() for each thread
        # it ensures that merging of parts occur only after each thread has completed downloading
        main_thread = threading.current_thread()
        for t in threading.enumerate():
            if t is main_thread:
                continue
            t.join()    

    def merge_multithreaded_download_parts(self):
        """ function to perform merging of parts performed by multiple threads on single system """
        # merging parts
        with open(self.filepath,'wb') as wfd:
            for f in range(self.threads):
                tempfilepath = constants.SERVER_TEMP_DIR + "/temp" + str(f)
                with open(tempfilepath, "rb") as fd:
                    shutil.copyfileobj(fd, wfd)     
                # delete copied segment
                misc.delete_file(tempfilepath)

    def download(self, url, range_left, range_right, filepath, response, threads):
        """
            function to perform file download
        """
        self.url = url
        self.range_right = range_right
        self.range_left = range_left
        self.filepath = filepath        
        self.threads = threads

        # if server supports segmented download
        if self.range_download_support(response):
            # get ranges for download for each thread
            ranges_list = calculation.get_download_ranges_list( self.range_left, 
                                                                self.range_right,
                                                                self.threads)
            # perform multithreaded download on single system
            self.multithreaded_download(ranges_list)
            # merge multithreaded download parts
            self.merge_multithreaded_download_parts()
        else:   
            misc.print_log ('''[i] Server doesn't support multithreaded downloads!
                Download will be performed using single thread, on master system.''')   
            request.download_range( self.url,
                                    self.filepath,
                                    self.range_left, 
                                    self.range_right)
