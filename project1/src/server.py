# import grpc
# import groupChat_pb2
# import groupChat_pb2_grpc
# from concurrent import futures
# import logging


# port = 8001


# class GroupChat(groupChat_pb2_grpc.ChatServerServicer):

#     def Login(self, request, context):
#         return groupChat_pb2.LoginResponse(status='Hello, %s!' % request.userName)


# def serve():
#     server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#     groupChat_pb2_grpc.add_ChatServerServicer_to_server(GroupChat(), server)
#     server.add_insecure_port('[::]:' + str(port))
#     server.start()
#     print("Server started, listening on " + str(port))
#     server.wait_for_termination()


# if __name__ == '__main__':
#     logging.basicConfig()
#     serve()

import grpc
import groupChat_pb2
import groupChat_pb2_grpc
from concurrent import futures
import time
port = 8001
timeSleep = 1


# The code are mainly for testing purpose
class ChatServer(groupChat_pb2_grpc.ChatServerServicer):
    def __init__(self):
        self.messages = []
        self.lastIndex = 0

    def getMessages(self, request, context):
        while self.lastIndex < len(self.messages):
            yield groupChat_pb2.ChatMessage(id=1, content=self.messages[self.lastIndex], numberOfLikes=0)
            self.lastIndex += 1
            time.sleep(timeSleep)

    def chatFunction(self, request_iterator, context):
        for request in request_iterator:
            if request.type == 3:
                self.messages.append(request.message)
                print("Message from client: {0}".format(request.message))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    groupChat_pb2_grpc.add_ChatServerServicer_to_server(ChatServer(), server)
    server.add_insecure_port('[::]:8001')
    server.start()
    print("Server started, listening on " + str(port))
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
