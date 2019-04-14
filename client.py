from __future__ import print_function
from multiprocessing import Pool

import ast
from concurrent import futures
import logging
import constants
import utils
import argparse
import pickle
import os
import time
import download
import math

import grpc

import discover_pb2
import discover_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
SELF_IP = utils.getNetworkIp()

ip_list = []

class Collaborator(discover_pb2_grpc.CollaboratorServicer):

    def SendMessage(self, request, context):
        message_type = request.message_type
        message = request.message
        utils.print_log('Received message of type: %d' % (message_type))
        utils.print_log('message: %s' % (message))
        raw_message = message.strip().split()
        if raw_message[0] == "request":
            return handle_request(raw_message)
        print(">")
        return discover_pb2.MessageReply(message_type=0, message="ack")

    def SendFileList(self, request, context):
        utils.print_log('Received file list request from %s' % (request.ip))
        local_files = os.listdir(constants.SHARED_FOLDER)
        return discover_pb2.FileListReply(file_list=pickle.dumps(local_files))

    def SendFile(self, request, context):
        utils.print_log('Received file request from %s' % (request.sender_ip))
        if request.is_local:
            f = open(constants.SHARED_FOLDER + '/' + request.file_name, 'rb')
            data = f.read()
            f.close()
            for i in range(request.start, request.end+1, constants.CHUNK_SIZE):
                yield data[i: min(request.end, i+constants.CHUNK_SIZE)+1]
        else:
            # TODO: unimplemented for remote file
            pass


def handle_request(raw_message):
    file_name = raw_message[1]
    is_file_local = search_file(file_name)
    if is_file_local:
        return discover_pb2.MessageReply(message_type=0, message="exists", sender_ip=SELF_IP)
    else:
        return discover_pb2.MessageReply(message_type=0, message="ready", sender_ip=SELF_IP)


def send(node, message, ip):
    try:
        utils.print_log("Sending message to %s..." % (node))
        channel = grpc.insecure_channel(node + ':' + str(constants.MESSAGING_PORT))
        stub = discover_pb2_grpc.CollaboratorStub(channel)
        response = stub.SendMessage(discover_pb2.MessageRequest(message_type=1, message=message, sender_ip=ip))
        utils.print_log("Sent message '%s' to node '%s'" % (message, node))
        utils.print_log("Received response '%s'" % (response.message))
        return response
    except Exception:
        utils.print_log("Could not send message to '%s'" % (node))
        return False


def broadcast(message):
    global ip_list
    utils.print_log("Broadcasting message '%s'..." % (message))
    response_list = []
    for node in ip_list:
        if node != SELF_IP:
            node_response = send(node, message, SELF_IP)
            if not node_response:
                ip_list.remove(node)
            else:
                response_list.append(node_response)
    utils.print_log("Broadcast message complete.")
    return response_list


def node_file_list(node):
    try:
        channel = grpc.insecure_channel(node + ':' + str(constants.MESSAGING_PORT))
        stub = discover_pb2_grpc.CollaboratorStub(channel)
        response = stub.SendFileList(discover_pb2.FileListRequest(ip=SELF_IP))
        return pickle.loads(ast.literal_eval(response))
    except Exception:
        utils.print_log('Could not retrieve file list from %s' % (node))
        return []


def filelist():
    global ip_list
    utils.print_log("Requsting files from collaborators")
    shared_files = []
    for node in ip_list:
        print('Node ', node)
        if node != SELF_IP:
            node_files = node_file_list(node)

            print('+++--- %s' % (node))
            print(node_files)
            for file in node_files:
                print(file)
        else:
            node_files = os.listdir(constants.SHARED_FOLDER)
            for file in node_files:
                print('Local: ', file)

    utils.print_log('Received following files from neighbors')


def search_file(file_name):
    for file in os.listdir(constants.DOWNLOAD_FOLDER):
        if os.path.basename(file) == file_name:
            return True
    return False


def request_download(file_url):
    file_name = download.get_file_name(file_url)
    response_list = broadcast('request ' + file_name)
    is_file_local = False
    local_nodes = []
    ready_nodes = []
    for response in response_list:
        if response.message == "exists":
            is_file_local = True
            local_nodes.append(response.sender_ip)
        elif response.message == "ready":
            ready_nodes.append(response.sender_ip)
    if is_file_local:
        delegate_download(file_url, local_nodes, True)
    else:
        delegate_download(file_url, ready_nodes, False)


def delegate_download(file_url, nodes_list, is_local):
    file_size = download.get_file_size_curl(file_url)
    if is_local:
        N = len(nodes_list)
        ranges_list = get_file_ranges(file_size, N)
        file_url_list = [file_url] * N
        with Pool(N) as p:
            p.map(get_local_files, zip(nodes_list, file_url_list, ranges_list))
    else:
        # Here, current node also downloads file
        N = len(nodes_list) + 1
        ranges_list = get_file_ranges(file_size, N)
        file_url_list = [file_url] * N
        with Pool(N) as p:
            p.map(get_remote_files, zip(nodes_list, file_url_list, ranges_list))


def get_file_ranges(file_size, num_nodes):
    ranges_list = []
    alloc_size = math.ceil(file_size/num_nodes)
    for i in range(num_nodes):
        ranges_list.append((i*alloc_size, min(file_size, (i+1)*alloc_size)))
    return ranges_list


def get_local_files(data_tuple):
    channel = grpc.insecure_channel(data_tuple[0] + ':' + str(constants.MESSAGING_PORT))
    stub = discover_pb2_grpc.CollaboratorStub(channel)
    utils.print_log('Connected to node %s' % (data_tuple[0]))
    file_name = download.get_file_name(data_tuple[1])
    response = stub.SendFiles(discover_pb2.FileRequest(sender_ip=SELF_IP, file_name=file_name, file_url=data_tuple[1], start=data_tuple[2][0], end=data_tuple[2][1], is_local=True))
    out_file = constants.DOWNLOAD_FOLDER + '/' + str(data_tuple[2][0]) + '-' +str(data_tuple[2][1]) + '-' + file_name
    file = open(out_file, 'w')
    file.write(response.file_chunk)
    file.close()
    utils.print_log('Completed download from %s' % (data_tuple[0]))


def get_remote_files(data_tuple):
    if data_tuple[2][0] == 0:   # If the current node is the requester
        download.download_file_curl(data_tuple[1], data_tuple[2][0], data_tuple[2][1], constants.DOWNLOAD_FOLDER)
    else:
        channel = grpc.insecure_channel(data_tuple[0] + ':' + str(constants.MESSAGING_PORT))
        stub = discover_pb2_grpc.CollaboratorStub(channel)
        utils.print_log('Connected to node %s' % (data_tuple[0]))
        file_name = download.get_file_name(data_tuple[1])
        response = stub.SendFiles(discover_pb2.FileRequest(sender_ip=SELF_IP, file_name=file_name, file_url=data_tuple[1], start=data_tuple[2][0], end=data_tuple[2][1], is_local=False))
        out_file = constants.DOWNLOAD_FOLDER + '/' + str(data_tuple[2][0]) + '-' +str(data_tuple[2][1]) + '-' + file_name
        file = open(out_file, 'w')
        file.write(response.file_chunk)
        file.close()
        utils.print_log("Completed chunk download from node %s" % (response.sender_ip))


def serve():
    global ip_list
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    discover_pb2_grpc.add_CollaboratorServicer_to_server(Collaborator(), server)
    server.add_insecure_port('[::]:' + str(constants.MESSAGING_PORT))
    server.start()
    utils.print_log('Starting collaborator node at IP ' + SELF_IP + ' with pid ' + str(os.getpid()))
    try:
        in_command_loop = True
        while in_command_loop:
            raw_input = input(">").strip().split()
            if raw_input[0] == "help":
                print("Available commands are: \n help, send <IP> <Message>, bcast <Message>, files, request <file_url>")
            elif raw_input[0] == "send":
                send(raw_input[1], raw_input[2], SELF_IP)
            elif raw_input[0] == "bcast":
                broadcast(raw_input[1])
            elif raw_input[0] == "request":
                request_download(raw_input[1])
            elif raw_input[0] == "files":
                filelist()

    except KeyboardInterrupt:
        utils.print_log("Stopping collaborator. Goodbye!")
        server.stop(0)


def run(discovery_ip):
    channel = grpc.insecure_channel(discovery_ip + ':' + str(constants.DISCOVERY_PORT))
    stub = discover_pb2_grpc.GreeterStub(channel)
    response = stub.GetNodes(discover_pb2.IdRequest(ip=SELF_IP))
    utils.print_log('Connected to server')
    global ip_list
    ip_list = pickle.loads(response.ip_list)
    utils.print_log('All discovered clients are:')
    for id, ip in enumerate(ip_list):
        utils.print_log("\tnode # %3d ip: %s" % (id+1, ip))
    serve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--discovery', action="store", dest="discovery_ip", type=str, help="Specify discovery server IP")
    args = parser.parse_args()

    utils.print_prompt()

    if args.discovery_ip:
        discovery_ip = args.discovery_ip
    else:
        print('Need to provide discovery server IP !')
        exit(0)

    utils.print_log('Starting connection to ' + discovery_ip)
    run(discovery_ip)
