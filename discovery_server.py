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

    def AssignId(self, request, context):
        address = request.ip
        utils.print_log('Receieved connection from ' + address)
        ip_list = []
        if os.path.exists(constants.LOG_FILE):
            with open(constants.LOG_FILE, 'rb') as f:
                ip_list = pickle.load(f)

        assign_id = len(ip_list) + 1

        # save ip in list, and update file
        ip_list.append(address)
        with open(constants.LOG_FILE, 'wb') as f:
            pickle.dump(ip_list, f)

        utils.print_log('Assigning id# ' + str(assign_id) + ' to ' + request.ip)
        return discover_pb2.IdReply(id=assign_id, ip_list=pickle.dumps(ip_list))


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
        print("Stopping discovery server. Goodbye!")
        server.stop(0)


if __name__ == '__main__':
    utils.print_prompt(discovery=True)
    serve()
