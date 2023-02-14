import asyncio
import grpc
import time
import threading
import groupChat_pb2
import groupChat_pb2_grpc
from concurrent import futures

# Chat room class to store information about a chat room


class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.users = {}
        self.messages = []

    #add an user, the key is uuid and the value is username
    def add_user(self, user, id):
        self.users[id] = user

    #remove an user, just remove the certain uuid's user, if there are two same username in a group, only remove one of them
    def remove_user(self, id):
        del self.users[id]

    def add_message(self, message):
        self.messages.append(message)

    def add_like(self, user, message_id):
        id = message_id - 1
        if id in range(len(self.messages)):
            message = self.messages[id]
        else:
            return False
        if user != message.user and user not in message.likes:
            message.likes.add(user)
            return True
        else:
            return False

    def remove_like(self, user, message_id):
        id = message_id - 1
        if id in range(len(self.messages)):
            message = self.messages[id]
        else:
            return False
        if user in message.likes:
            message.likes.remove(user)
            return True
        else:
            return False

#For every message, there is a message id, user who wrote it, message content and a set of data who liked it
class ChatMessage:
    def __init__(self, id, user, message):
        self.id = id
        self.user = user
        self.message = message
        self.likes = set()


class ChatService(groupChat_pb2_grpc.ChatServerServicer):
    def __init__(self):
        self.users = {}
        self.groups = {}
        self.lastId = {}

    def chatFunction(self, request, context):
        # type 1: login, 2: join, 3: chat, 4: like, 5: dislike, 6: history
        try:
            _type = request.type
        except ValueError:
            print("Error type")
        if _type == 1:
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 2:
            #if the user joined another group, we need to remove it from that group
            if request.uuid in self.users and self.users[request.uuid] in self.groups:
                self.groups[self.users[request.uuid]].remove_user(request.uuid)
            if request.groupName not in self.groups.keys():
                self.groups[request.groupName] = ChatRoom(request.groupName)
            self.groups[request.groupName].add_user(
                request.userName, request.uuid)
            self.users[request.uuid] = request.groupName
            return groupChat_pb2.ChatOutput(status="success", messages=[], user=list(set(self.groups[request.groupName].users.values())))
        elif _type == 3:
            chatRoom = self.groups[request.groupName]
            chatRoom.add_message(ChatMessage(len(chatRoom.messages) + 1, request.userName, request.message))
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 4:
            chatRoom = self.groups[request.groupName]
            if not chatRoom.add_like(request.userName, request.messageId):
                return groupChat_pb2.ChatOutput(status="success", messages=[])
            #only when the message user liked is within lastest 10 message, we need to refresh the message list
            if request.messageId > len(chatRoom.messages) - 10:
                for element in self.lastId:
                    if self.lastId[element] > 0:
                        self.lastId[element] = self.lastId[element] - 1
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 5:
            chatRoom = self.groups[request.groupName]
            if not chatRoom.remove_like(request.userName, request.messageId):
                return groupChat_pb2.ChatOutput(status="success", messages=[])
            if request.messageId > len(chatRoom.messages) - 10:
                for element in self.lastId:
                    if self.lastId[element] > 0:
                        self.lastId[element] = self.lastId[element] - 1
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        elif _type == 6:
            chatRoom = self.groups[request.groupName]
            message = chatRoom.messages
            msg_list = []
            for message in chatRoom.messages:
                msg_list.append(groupChat_pb2.ChatMessage(
                    id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes)))
            return groupChat_pb2.ChatOutput(status="success", messages=msg_list)
        elif _type == 7:
            self.groups[request.groupName].remove_user(request.uuid)
            return groupChat_pb2.ChatOutput(status="success", messages=[])
        else:
            return groupChat_pb2.ChatOutput(status="failed", messages=[])

    def getMessages(self, request, context):
        self.lastId[request.uuid] = 0
        while(True):
            #if the user has joined another group, remove it
            if request.uuid not in self.groups[request.groupName].users.keys():
                yield groupChat_pb2.ChatMessage(id=-999, user="", content="", numberOfLikes=0)
                break
            lastId = self.lastId[request.uuid]
            chatRoom = self.groups[request.groupName]
            #if the client crashed, remove the user
            if not context.is_active():
                chatRoom.remove_user(request.uuid)
                break
            if len(chatRoom.messages) > lastId:
                self.lastId[request.uuid] = len(chatRoom.messages)
                for message in chatRoom.messages[-10:]:
                    yield groupChat_pb2.ChatMessage(id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes))


def start_server(port: int):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    groupChat_pb2_grpc.add_ChatServerServicer_to_server(ChatService(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, args=(8001,))
    server_thread.start()
    print("Server started on port 8001! ")

    # Start the event loop
    loop = asyncio.get_event_loop()
    loop.run_forever()
