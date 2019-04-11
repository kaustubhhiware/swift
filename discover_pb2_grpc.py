# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import discover_pb2 as discover__pb2


class GreeterStub(object):
  """The greeting service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetNodes = channel.unary_unary(
        '/discover.Greeter/GetNodes',
        request_serializer=discover__pb2.IdRequest.SerializeToString,
        response_deserializer=discover__pb2.IdReply.FromString,
        )


class GreeterServicer(object):
  """The greeting service definition.
  """

  def GetNodes(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_GreeterServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetNodes': grpc.unary_unary_rpc_method_handler(
          servicer.GetNodes,
          request_deserializer=discover__pb2.IdRequest.FromString,
          response_serializer=discover__pb2.IdReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'discover.Greeter', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class CollaboratorStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.SendMessage = channel.unary_unary(
        '/discover.Collaborator/SendMessage',
        request_serializer=discover__pb2.MessageRequest.SerializeToString,
        response_deserializer=discover__pb2.MessageReply.FromString,
        )
    self.SendFiles = channel.unary_unary(
        '/discover.Collaborator/SendFiles',
        request_serializer=discover__pb2.FileListRequest.SerializeToString,
        response_deserializer=discover__pb2.FileListReply.FromString,
        )


class CollaboratorServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def SendMessage(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def SendFiles(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_CollaboratorServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'SendMessage': grpc.unary_unary_rpc_method_handler(
          servicer.SendMessage,
          request_deserializer=discover__pb2.MessageRequest.FromString,
          response_serializer=discover__pb2.MessageReply.SerializeToString,
      ),
      'SendFiles': grpc.unary_unary_rpc_method_handler(
          servicer.SendFiles,
          request_deserializer=discover__pb2.FileListRequest.FromString,
          response_serializer=discover__pb2.FileListReply.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'discover.Collaborator', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
