from __future__ import print_function
import logging
import constants
import utils
import argparse
import pickle

import grpc

import discover_pb2
import discover_pb2_grpc

SELF_IP = utils.getNetworkIp()

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
    exit(0)


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

    utils.print_log('Starting connection to ' + SELF_IP)
    run(discovery_ip)
