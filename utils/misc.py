import socket
import time
import os
import shutil


def print_welcome_prompt(discovery=False):
    file = 'utils/prompt_discovery' if discovery else 'utils/prompt' 
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
    print(time.strftime('[%d %b %Y - %H:%M:%S]') + str(message))


def get_file_size_local(file):
    '''
        get local file size. Useful for heartbeat.
    '''
    if not os.path.exists(file):
        return -1

    statinfo = os.stat(file)
    return statinfo.st_size


#### FILE HANDLING

def delete_file(filepath):
    if not os.path.exists(filepath):
        return
    try:
        os.remove(filepath)
    except Exception as err:
        print_log('[!] Error in deleting file ', err)


def create_dir(dirpath):
    if os.path.exists(dirpath):
        return
    try:
        os.makedirs(dirpath)
    except Exception as err:
        print_log('[!] Error in creating dir ', err)

def delete_dir(dirpath):
    """
        recursive deletion of a directory at dirpath
    """
    if not os.path.exists(dirpath):
        return
    try:
        shutil.rmtree(dirpath)
    except Exception as err:
        print_log('[!] Error in deleting dir ', err)


#### FILE HANDLING