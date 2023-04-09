# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import raft_pb2 as raft__pb2


class RaftStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.RequestVote = channel.unary_unary(
                '/raft.Raft/RequestVote',
                request_serializer=raft__pb2.VoteRequest.SerializeToString,
                response_deserializer=raft__pb2.VoteResponse.FromString,
                )
        self.AppendEntries = channel.unary_unary(
                '/raft.Raft/AppendEntries',
                request_serializer=raft__pb2.AppendEntriesRequest.SerializeToString,
                response_deserializer=raft__pb2.AppendEntriesResponse.FromString,
                )
        self.AddServer = channel.unary_unary(
                '/raft.Raft/AddServer',
                request_serializer=raft__pb2.AddServerRequest.SerializeToString,
                response_deserializer=raft__pb2.AddServerResponse.FromString,
                )
        self.RemoveServer = channel.unary_unary(
                '/raft.Raft/RemoveServer',
                request_serializer=raft__pb2.RemoveServerRequest.SerializeToString,
                response_deserializer=raft__pb2.RemoveServerResponse.FromString,
                )
        self.ClientRequest = channel.unary_unary(
                '/raft.Raft/ClientRequest',
                request_serializer=raft__pb2.ClientAppendRequest.SerializeToString,
                response_deserializer=raft__pb2.ClientAppendResponse.FromString,
                )
        self.RegisterClient = channel.unary_unary(
                '/raft.Raft/RegisterClient',
                request_serializer=raft__pb2.RegisterClientRequest.SerializeToString,
                response_deserializer=raft__pb2.RegisterClientResponse.FromString,
                )
        self.ClientQuery = channel.unary_unary(
                '/raft.Raft/ClientQuery',
                request_serializer=raft__pb2.ClientQueryRequest.SerializeToString,
                response_deserializer=raft__pb2.ClientQueryResponse.FromString,
                )


class RaftServicer(object):
    """Missing associated documentation comment in .proto file."""

    def RequestVote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AppendEntries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddServer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RemoveServer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ClientRequest(self, request, context):
        """sennd from client to leader server
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RegisterClient(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ClientQuery(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RaftServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'RequestVote': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestVote,
                    request_deserializer=raft__pb2.VoteRequest.FromString,
                    response_serializer=raft__pb2.VoteResponse.SerializeToString,
            ),
            'AppendEntries': grpc.unary_unary_rpc_method_handler(
                    servicer.AppendEntries,
                    request_deserializer=raft__pb2.AppendEntriesRequest.FromString,
                    response_serializer=raft__pb2.AppendEntriesResponse.SerializeToString,
            ),
            'AddServer': grpc.unary_unary_rpc_method_handler(
                    servicer.AddServer,
                    request_deserializer=raft__pb2.AddServerRequest.FromString,
                    response_serializer=raft__pb2.AddServerResponse.SerializeToString,
            ),
            'RemoveServer': grpc.unary_unary_rpc_method_handler(
                    servicer.RemoveServer,
                    request_deserializer=raft__pb2.RemoveServerRequest.FromString,
                    response_serializer=raft__pb2.RemoveServerResponse.SerializeToString,
            ),
            'ClientRequest': grpc.unary_unary_rpc_method_handler(
                    servicer.ClientRequest,
                    request_deserializer=raft__pb2.ClientAppendRequest.FromString,
                    response_serializer=raft__pb2.ClientAppendResponse.SerializeToString,
            ),
            'RegisterClient': grpc.unary_unary_rpc_method_handler(
                    servicer.RegisterClient,
                    request_deserializer=raft__pb2.RegisterClientRequest.FromString,
                    response_serializer=raft__pb2.RegisterClientResponse.SerializeToString,
            ),
            'ClientQuery': grpc.unary_unary_rpc_method_handler(
                    servicer.ClientQuery,
                    request_deserializer=raft__pb2.ClientQueryRequest.FromString,
                    response_serializer=raft__pb2.ClientQueryResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'raft.Raft', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Raft(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def RequestVote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/RequestVote',
            raft__pb2.VoteRequest.SerializeToString,
            raft__pb2.VoteResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AppendEntries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/AppendEntries',
            raft__pb2.AppendEntriesRequest.SerializeToString,
            raft__pb2.AppendEntriesResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/AddServer',
            raft__pb2.AddServerRequest.SerializeToString,
            raft__pb2.AddServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RemoveServer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/RemoveServer',
            raft__pb2.RemoveServerRequest.SerializeToString,
            raft__pb2.RemoveServerResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ClientRequest(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/ClientRequest',
            raft__pb2.ClientAppendRequest.SerializeToString,
            raft__pb2.ClientAppendResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RegisterClient(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/RegisterClient',
            raft__pb2.RegisterClientRequest.SerializeToString,
            raft__pb2.RegisterClientResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ClientQuery(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raft.Raft/ClientQuery',
            raft__pb2.ClientQueryRequest.SerializeToString,
            raft__pb2.ClientQueryResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
