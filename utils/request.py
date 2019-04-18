"""
    Handles requests
"""
import sys
import urllib3
from utils import constants
from utils import misc

def make_request(url, retries=5, timeout=5, headers=None):
    """ function for sending request and receiving response """
    http = urllib3.ProxyManager(constants.PROXY)

    try:
        resp = http.request("GET", 
            url.replace("https", "http"), 
            retries=retries, 
            timeout=timeout,
            preload_content=False,
            headers=headers)
    except urllib3.exceptions.NewConnectionError:
        # if failed to create connection
        misc.print_log ("[!] Connection failed in make_request !")
    except urllib3.exceptions.SSLError:
        # if failed to establish secure connection (https)
        misc.print_log ("[!] SSL Error in make_request !")

    return resp


def download_range(url, filepath, range_left, range_right):
    resp = make_request(url, headers={'Range': 'bytes=%d-%d' % (range_left, range_right)})

    with open(filepath, "wb") as fp:
        downloaded = 0 #in KBs
        while True:
            data = resp.read(constants.DOWNLOAD_CHUNK_SIZE)
            if not data:
                misc.print_log ("\n[i] Download Finished.")
                break
            fp.write(data)
            downloaded += sys.getsizeof(data) 
            print ("\r[i] {0:.2f} MB".format(downloaded/(1024*1024)), end="")

    close_connection(resp)

def close_connection(response):
    response.release_conn()


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