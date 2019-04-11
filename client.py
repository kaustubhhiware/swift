from __future__ import print_function
import ast
from concurrent import futures
import logging
import constants
import utils
import argparse
import pickle
import os
import time

import grpc

import discover_pb2
import discover_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
SELF_IP = utils.getNetworkIp()

class Collaborator(discover_pb2_grpc.CollaboratorServicer):

    def SendMessage(self, request, context):
        message_type = request.message_type
        message = request.message
        utils.print_log('Received message of type: %d' % (message_type))
        utils.print_log('message: %s' % (message))
        return discover_pb2.MessageReply(message_type=0, message="ack")


    def SendFiles(self, request, context):
        utils.print_log('Received file list request from %s' % (request.ip))
        local_files = os.listdir(constants.SHARED_FOLDER)
        return discover_pb2.FileListReply(file_list=pickle.dumps(local_files))


def send(node, message):
    try:
        utils.print_log("Sending message to %s..." % (node))
        channel = grpc.insecure_channel(node + ':' + str(constants.MESSAGING_PORT))
        stub = discover_pb2_grpc.CollaboratorStub(channel)
        response = stub.SendMessage(discover_pb2.MessageRequest(message_type=1, message=message))
        utils.print_log("Sent message '%s' to node '%s'" % (message, node))
        utils.print_log("Received response '%s'" % (response.message))
        return True
    except Exception:
        utils.print_log("Could not send message to '%s'" % (node))
        return False


def broadcast(message, ip_list):
    utils.print_log("Broadcasting message '%s'..." % (message))
    for node in ip_list:
        if node != SELF_IP:
            is_active = send(node, message)
            if not is_active:
                ip_list.remove(node)
    utils.print_log("Broadcast message complete.")


def node_file_list(node):
    try:
        channel = grpc.insecure_channel(node + ':' + str(constants.MESSAGING_PORT))
        stub = discover_pb2_grpc.CollaboratorStub(channel)
        response = stub.SendFiles(discover_pb2.FileRequest(ip=SELF_IP))
        return pickle.loads(ast.literal_eval(response))
    except Exception:
        utils.print_log('Could not retrieve file list from %s' % (node))
        return []


def filelist(ip_list):
    utils.print_log("Requsting files from collaborators")
    shared_files = []
    for node in ip_list:
        if node != SELF_IP:
            node_files = node_file_list(node)

            if node_files is None:
                continue
            for file in node_files:
                print(file)

    utils.print_log('Received following files from neighbors')


def serve(ip_list):
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
                print("Available commands are: \n help, send <IP> <Message>, bcast <Message>, files")
            elif raw_input[0] == "send":
                send(raw_input[1], raw_input[2])
            elif raw_input[0] == "bcast":
                broadcast(raw_input[1], ip_list)

            elif raw_input[0] == "files":
                filelist(ip_list)

    except KeyboardInterrupt:
        utils.print_log("Stopping collaborator. Goodbye!")
        server.stop(0)


def run(discovery_ip):
    channel = grpc.insecure_channel(discovery_ip + ':' + str(constants.DISCOVERY_PORT))
    stub = discover_pb2_grpc.GreeterStub(channel)
    response = stub.GetNodes(discover_pb2.IdRequest(ip=SELF_IP))
    utils.print_log('Connected to server')
    ip_list = pickle.loads(response.ip_list)
    utils.print_log('All discovered clients are:')
    for id, ip in enumerate(ip_list):
        utils.print_log("\tnode # %3d ip: %s" % (id+1, ip))
    serve(ip_list)


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
