from atexit import register
from concurrent import futures
from os.path import isfile
from math import ceil
from random import random, uniform
from google.protobuf.json_format import MessageToJson, Parse
from time import time, sleep
import enum
import grpc
import sys
import group_chat_pb2
import group_chat_pb2_grpc
import threading
import asyncio
import json
import argparse

DEBUG = False

class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.users = {}
        self.messages = []

    # add an user, the key is uuid and the value is username
    def add_user(self, user, id):
        self.users[id] = user

    # remove an user, just remove the certain uuid's user, if there are two same username in a group, only remove one of them
    def remove_user(self, id):
        if id in self.users:
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

# For every message, there is a message id, user who wrote it, message content and a set of data who liked it


class ChatMessage:
    def __init__(self, id, user, message):
        self.id = id
        self.user = user
        self.message = message
        self.likes = set()


class ChatRoomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ChatMessage):
            return {
                'id': obj.id,
                'user': obj.user,
                'message': obj.message,
                'likes': list(obj.likes)
            }
        elif isinstance(obj, ChatRoom):
            return {
                'name': obj.name,
                'users': obj.users,
                'messages': obj.messages
            }
        return super(ChatRoomEncoder, self).default(obj)


def groups_decoder(json_data):
    groups = {}
    for key, room_data in json_data.items():
        room = ChatRoom(room_data['name'])
        room.users = room_data['users']
        for message_data in room_data['messages']:
            message = ChatMessage(
                message_data['id'], message_data['user'], message_data['message'])
            message.likes = set(message_data['likes'])
            room.messages.append(message)
        groups[key] = room
    return groups


def log_encoder(log):
    return {key: MessageToJson(log[key]) for key in log.keys()}


def log_decoder(json_dict):
    log = {}
    for key in json_dict.keys():
        grpc_msg = Parse(json_dict[key], group_chat_pb2.Entry())
        log[int(key)] = grpc_msg
    return log


class ChatServer(group_chat_pb2_grpc.ChatServerServicer()):
    # Initialization.
    def __init__(self, server_address, server_id):
        self.users = {}
        self.groups = {}
        self.lastId = {}
        self.id = server_id
        self.vector = [0] * len(server_address)
        self.log = {}
        self.peers_address = {
            _id: server_address[_id] for _id in server_address.keys() if _id != self.id}
        self.stubs = {_id: group_chat_pb2_grpc.ChatServerStub(grpc.insecure_channel(
            server_address[_id])) for _id in server_address.keys() if _id != self.id}

        self.decodeFromFile()

    def decodeFromFile(self):
        server_id = self.id
        if (isfile(f'./logs/log_{server_id}.json')):
            with open(f'./logs/log_{server_id}.json', 'r') as fp:
                self.log = log_decoder(json.load(fp))
                printLog("Decode log success")

        if (isfile(f'./logs/groups_{server_id}.json')):
            with open(f'./logs/groups_{server_id}.json', 'r') as fp:
                self.groups = groups_decoder(json.load(fp))

        if (isfile(f'./logs/users_{server_id}.json')):
            with open(f'./logs/users_{server_id}.json', 'r') as fp:
                self.users = json.load(fp)
        if (isfile(f'./logs/lastId_{server_id}.json')):
            with open(f'./logs/lastId_{server_id}.json', 'r') as fp:
                self.lastId = json.load(fp)

    def chatFunction(self, request, context):
        # type 1: login, 2: join, 3: chat, 4: like, 5: dislike, 6: history
        self.last_log_term = self.term
        self.last_log_idx += 1
        sync_thread = threading.Thread(target=syncServer, args=(request))
        sync_thread.start()
        response = self.processClientRequest(request)
        return response

    def syncServer(req):
        for id in self.stubs.keys():
            stub = self.stubs[id]
            try:
                response = stub.AppendEntries(req)
            except grpc.RpcError as e:
                printLog('Chatfunction:cannot connect to ' +
                      str(self.peers_address[id]))

    def processClientRequest(self, request):
        try:
            _type = request.type
            if _type == 1:
                # if the user joined another group, we need to remove it from that group
                if request.uuid in self.users and self.users[request.uuid] in self.groups:
                    self.groups[self.users[request.uuid]].remove_user(request.uuid)
                return group_chat_pb2.ChatOutput(status="success", messages=[])
            elif _type == 2:
                # if the user joined another group, we need to remove it from that group
                if request.uuid in self.users and self.users[request.uuid] in self.groups:
                    self.groups[self.users[request.uuid]].remove_user(request.uuid)
                if request.groupName not in self.groups.keys():
                    self.groups[request.groupName] = ChatRoom(
                        request.groupName)
                self.groups[request.groupName].add_user(
                    request.userName, request.uuid)
                self.users[request.uuid] = request.groupName
                return group_chat_pb2.ChatOutput(status="success", messages=[], user=list(set(self.groups[request.groupName].users.values())))
            elif _type == 3:
                chatRoom = self.groups[request.groupName]
                chatRoom.add_message(ChatMessage(
                    len(chatRoom.messages) + 1, request.userName, request.message))
                return group_chat_pb2.ChatOutput(status="success", messages=[])
            elif _type == 4:
                chatRoom = self.groups[request.groupName]
                if not chatRoom.add_like(request.userName, request.messageId):
                    return group_chat_pb2.ChatOutput(status="success", messages=[])
                # only when the message user liked is within lastest 10 message, we need to refresh the message list
                if request.messageId > len(chatRoom.messages) - 10:
                    for element in self.lastId:
                        if self.lastId[element] > 0:
                            self.lastId[element] = self.lastId[element] - 1
                return group_chat_pb2.ChatOutput(status="success", messages=[])
            elif _type == 5:
                chatRoom = self.groups[request.groupName]
                if not chatRoom.remove_like(request.userName, request.messageId):
                    return group_chat_pb2.ChatOutput(status="success", messages=[])
                if request.messageId > len(chatRoom.messages) - 10:
                    for element in self.lastId:
                        if self.lastId[element] > 0:
                            self.lastId[element] = self.lastId[element] - 1
                return group_chat_pb2.ChatOutput(status="success", messages=[])
            elif _type == 6:
                chatRoom = self.groups[request.groupName]
                message = chatRoom.messages
                msg_list = []
                for message in chatRoom.messages:
                    msg_list.append(group_chat_pb2.ChatMessage(
                        id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes)))
                return group_chat_pb2.ChatOutput(status="success", messages=msg_list)
            elif _type == 7:
                # if the user joined another group, we need to remove it from that group
                if request.uuid in self.users and self.users[request.uuid] in self.groups:
                    self.groups[self.users[request.uuid]].remove_user(request.uuid)
                return group_chat_pb2.ChatOutput(status="success", messages=[])
            elif _type == 8:
                return group_chat_pb2.ChatOutput(status="success", messages=[group_chat_pb2.ChatMessage(content=str(self.leader_id))])
            else:
                return group_chat_pb2.ChatOutput(status="failed", messages=[])
        except ValueError:
            printLog("Error type")

    def getMessages(self, request, context):
        if request.uuid not in self.lastId.keys():
            self.lastId[request.uuid] = 0
        lastParticipants = len(
            list(set(self.groups[request.groupName].users.values())))
        while (True):
            # if the user has joined another group, remove it
            if request.uuid not in self.groups[request.groupName].users.keys():
                yield group_chat_pb2.ChatMessage(id=-999, user="", content="", numberOfLikes=0)
                self.lastId[request.uuid] = 0
                break
            lastId = self.lastId[request.uuid]
            chatRoom = self.groups[request.groupName]
            # if the client crashed, remove the user
            if not context.is_active():
                chatRoom.remove_user(request.uuid)
                break
            # if number of participants changed
            participants = list(
                set(self.groups[request.groupName].users.values()))
            if (lastParticipants != len(participants)):
                lastParticipants = len(participants)
                yield group_chat_pb2.ChatMessage(id=-998, user=", ".join(participants), content=request.groupName, numberOfLikes=0)
            if len(chatRoom.messages) > lastId:
                self.lastId[request.uuid] = len(chatRoom.messages)
                for message in chatRoom.messages[-10:]:
                    yield group_chat_pb2.ChatMessage(id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes))


def saveToDisk(server_id, chatServer):
    printLog("Writing...")
    with open(f'./logs/log_{server_id}.json', 'w') as f:
        json.dump(log_encoder(chatServer.log), f, indent=4)
    with open(f'./logs/groups_{server_id}.json', 'w') as f:
        json.dump(chatServer.groups, f, indent=4, cls=ChatRoomEncoder)
    with open(f'./logs/users_{server_id}.json', 'w') as f:
        json.dump(chatServer.users, f)
    with open(f'./logs/lastId_{server_id}.json', 'w') as f:
        json.dump(chatServer.lastId, f)


def start_server():
    server_address = {}
    if DEBUG:
        filename = "./config.json"
    else:
        filename = "./config_test.json"
    with open(filename, 'r') as f:
        addr_dict = json.load(f)
        for key, value in addr_dict.items():
            server_address[int(key)] = value
    printLog(server_address)
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Server id")
    parser.add_argument("-D", help="Debug")
    args = parser.parse_args()
    if args.id is None:
        print(
            "Please specify server id with command : python server.py -id [id]")
        sys.exit(1)
    if args.D is None:
        DEBUG = True
    server_id = int(args.id)
    chatServer = ChatServer(server_address, server_id)
    server = grpc.server(futures.ThreadPoolExecutor())
    group_chat_pb2_grpc.add_ChatServerServicer_to_server(chatServer, server)
    host, port = server_address[server_id].split(":")
    print(f"Server started on port {port}! ")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    register(saveToDisk, server_id, chatServer)

def printLog(msg):
    if DEBUG:
        print(msg)

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
