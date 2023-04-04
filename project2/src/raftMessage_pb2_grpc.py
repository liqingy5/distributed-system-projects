# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import raftMessage_pb2 as raftMessage__pb2


class raftMessageStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.requestVote = channel.unary_unary(
                '/raftMessage.raftMessage/requestVote',
                request_serializer=raftMessage__pb2.RequestVoteArgs.SerializeToString,
                response_deserializer=raftMessage__pb2.RequestVoteReply.FromString,
                )
        self.appendEntries = channel.unary_unary(
                '/raftMessage.raftMessage/appendEntries',
                request_serializer=raftMessage__pb2.AppendEntriesArgs.SerializeToString,
                response_deserializer=raftMessage__pb2.AppendEntriesReply.FromString,
                )


class raftMessageServicer(object):
    """Missing associated documentation comment in .proto file."""

    def requestVote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def appendEntries(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_raftMessageServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'requestVote': grpc.unary_unary_rpc_method_handler(
                    servicer.requestVote,
                    request_deserializer=raftMessage__pb2.RequestVoteArgs.FromString,
                    response_serializer=raftMessage__pb2.RequestVoteReply.SerializeToString,
            ),
            'appendEntries': grpc.unary_unary_rpc_method_handler(
                    servicer.appendEntries,
                    request_deserializer=raftMessage__pb2.AppendEntriesArgs.FromString,
                    response_serializer=raftMessage__pb2.AppendEntriesReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'raftMessage.raftMessage', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class raftMessage(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def requestVote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raftMessage.raftMessage/requestVote',
            raftMessage__pb2.RequestVoteArgs.SerializeToString,
            raftMessage__pb2.RequestVoteReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def appendEntries(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/raftMessage.raftMessage/appendEntries',
            raftMessage__pb2.AppendEntriesArgs.SerializeToString,
            raftMessage__pb2.AppendEntriesReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
