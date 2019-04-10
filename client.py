from __future__ import print_function
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


def serve():
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
                print("Available commands are: \n help, send <IP> <Message>")
            elif raw_input[0] == "send":
                utils.print_log("Sending message to %s" % (raw_input[1]))
                channel = grpc.insecure_channel(raw_input[1] + ':' + str(constants.MESSAGING_PORT))
                stub = discover_pb2_grpc.CollaboratorStub(channel)
                response = stub.SendMessage(discover_pb2.MessageRequest(message_type=1, message=raw_input[2]))
                utils.print_log("Sent message '%s' to node '%s'" % (raw_input[2], raw_input[1]))
        # while True:
        #     time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print("Stopping collaborator. Goodbye!")
        server.stop(0)


def run(discovery_ip):
    channel = grpc.insecure_channel(discovery_ip + ':' + str(constants.DISCOVERY_PORT))
    stub = discover_pb2_grpc.GreeterStub(channel)
    response = stub.AssignId(discover_pb2.IdRequest(ip=SELF_IP))
    utils.print_log('Connected to server')
    utils.print_log('Id assigned by server is: ' + str(response.id))
    ip_list = pickle.loads(response.ip_list)
    utils.print_log('All discovered clients are:')
    for id, ip in enumerate(ip_list):
        utils.print_log("\tid# %3d ip: %s" % (id+1, ip))
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
