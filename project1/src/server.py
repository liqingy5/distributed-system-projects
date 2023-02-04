import grpc
import groupChat_pb2
import groupChat_pb2_grpc
from concurrent import futures
import logging


port = 8001


class GroupChat(groupChat_pb2_grpc.ChatServerServicer):

    def Login(self, request, context):
        return groupChat_pb2.LoginResponse(status='Hello, %s!' % request.userName)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    groupChat_pb2_grpc.add_ChatServerServicer_to_server(GroupChat(), server)
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    print("Server started, listening on " + str(port))
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
