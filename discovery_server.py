from concurrent import futures
import time
import logging
import constants
import utils
import os
import pickle

import grpc

import discover_pb2
import discover_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
SELF_IP = utils.getNetworkIp()


class Greeter(discover_pb2_grpc.GreeterServicer):

    def GetNodes(self, request, context):
        address = request.ip
        utils.print_log('Receieved connection from ' + address)
        ip_list = []
        if os.path.exists(constants.LOG_FILE):
            with open(constants.LOG_FILE, 'rb') as f:
                ip_list = pickle.load(f)

        # save ip in list, and update file
        ip_list.append(address)
        ip_list = list(set(ip_list))
        with open(constants.LOG_FILE, 'wb') as f:
            pickle.dump(ip_list, f)

        utils.print_log('Sending nodes IP address list to ' + request.ip)
        return discover_pb2.IdReply(ip_list=pickle.dumps(ip_list))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    discover_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:' + str(constants.DISCOVERY_PORT))
    server.start()
    utils.print_log('Starting discovery server at IP ' + SELF_IP + ' with pid ' + str(os.getpid()))
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        utils.print_log("Stopping discovery server. Goodbye!")
        server.stop(0)


if __name__ == '__main__':
    utils.print_prompt(discovery=True)
    serve()
