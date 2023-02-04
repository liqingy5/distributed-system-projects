import grpc
import groupChat_pb2
import groupChat_pb2_grpc
import logging


address = 'localhost'
port = 8001


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    print("Connect to Server")
    with grpc.insecure_channel(address + ':' + str(port)) as channel:
        stub = groupChat_pb2_grpc.ChatServerStub(channel)
        response = stub.Login(groupChat_pb2.LoginRequest(userName='qingyang'))
    print("Group client received: " + response.status)


if __name__ == '__main__':
    logging.basicConfig()
    run()
