import grpc
import time
import threading
import groupChat_pb2
import groupChat_pb2_grpc
from concurrent import futures
import json

# Chat room class to store information about a chat room
class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.users = set()
        self.messages = []
        self.lastId = 0
    
    def add_message(self, message):
        self.messages.append(message)
    
    def add_like(self, user, message_id):
        message = self.messages[message_id]
        if user not in message.likes:
            message.likes.add(user)
    
    def remove_like(self, user, message_id):
        message = self.messages[message_id]
        if user in message.likes:
            message.likes.remove(user)

class ChatMessage:
    def __init__(self, id, message):
        self.id = id
        self.message = message
        self.like = set()

class ChatService(groupChat_pb2_grpc.ChatServerServicer):
    def __init__(self):
        self.users = set()
        self.groups = {}

    def chatFunction(self, request, context):
        #type 1: login, 2: join, 3: chat, 4: like, 5: dislike, 6: history
        print(request)
        try:
            _type = request.type
        except ValueError:
            print("Error type")
        if _type == 1:
            self.users.add(request.userName)
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 2:
            if request.groupName not in self.groups.keys():
                self.groups[request.groupName] = ChatRoom(request.groupName)
            self.groups[request.groupName].users.add(request.userName)
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 3:
            chatRoom = self.groups[request.groupName]
            chatRoom.add_message(ChatMessage(len(chatRoom.messages), request.message))
            msg_list = []
            for message in chatRoom.messages[-10:]:
                msg_list.append(groupChat_pb2.ChatMessage(id=message.id, content=message.message, numberOfLikes=len(message.like)))
            return groupChat_pb2.ChatOutput(status="success", messages=msg_list)
        elif _type == 4:
            chatRoom = self.groups[request.groupName]
            message = chatRoom.messages[request.messageId]
            message.add_like(request.userName)
            if request.messageId > len(chatRoom.messages) - 10:
                for message in chatRoom.messages[-10:]:
                    msg_list.append(groupChat_pb2.ChatMessage(id=message.id, content=message.message, numberOfLikes=len(message.like)))
                return groupChat_pb2.ChatOutput(status="success", messages=msg_list)
            else:
                return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 5:
            chatRoom = self.groups[request.groupName]
            message = chatRoom.messages[request.messageId]
            message.remove_like(request.userName)
            if request.messageId > len(chatRoom.messages) - 10:
                for message in chatRoom.messages[-10:]:
                    msg_list.append(groupChat_pb2.ChatMessage(id=message.id, content=message.message, numberOfLikes=len(message.like)))
                return groupChat_pb2.ChatOutput(status="success", messages=msg_list)
            else:
                return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 6:
            chatRoom = self.groups[request.groupName]
            message = chatRoom.messages
            for message in chatRoom.messages:
                msg_list.append(groupChat_pb2.ChatMessage(id=message.id, content=message.message, numberOfLikes=len(message.like)))
            return groupChat_pb2.ChatOutput(status="success", messages=msg_list)
        elif _type == 7:
            self.users.remove(request.userName)
            self.groups[request.groupName].users.remove(request.userName)
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        else:
            return groupChat_pb2.ChatOutput(status="failed", messages=[])

    def getMessages(self, request, context):
        while(True):
            chatRoom = self.groups[request.groupName]
            if len(chatRoom.messages) > chatRoom.lastId:
                print(chatRoom.lastId)
                chatRoom.lastId = len(chatRoom.messages)
                for message in chatRoom.messages[-10:]:
                    yield groupChat_pb2.ChatMessage(id=message.id, content=message.message, numberOfLikes=len(message.like))

if __name__ == '__main__':
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    groupChat_pb2_grpc.add_ChatServerServicer_to_server(ChatService(), server)
    server.add_insecure_port('[::]:8001')
    server.start()
    while True:
        time.sleep(64 * 64 * 100)