from concurrent import futures
from os.path import isfile
from google.protobuf.json_format import MessageToJson, Parse
import grpc
import sys
import group_chat_pb2
import group_chat_pb2_grpc
import threading
import asyncio
import json
import argparse
import os
from hold_back_queue import HoldBackQueue
import logging

logger = logging.getLogger()

DEBUG = False
TIME_OUT = 0.5


def isConcurrent(r_vt, s_vt):
    greater, smaller = False, False
    for i in range(len(r_vt)):
        if r_vt[i] > s_vt[i]:
            greater = True
        elif r_vt[i] < s_vt[i]:
            smaller = True

    if greater and smaller:
        return "concurrent"
    if greater:
        return "greater"
    else:
        return "smaller"


def Max(r_vt, s_vt):
    return [max(r_vt[i], s_vt[i]) for i in range(len(r_vt))]


class ChatRoom:
    def __init__(self, name):
        self.name = name
        self.users = {}
        self.messages = []

    # add an user, the key is uuid and the value is username
    def add_user(self, user, msgId, server_id):
        self.users[msgId] = (user, server_id)

    # remove an user, just remove the certain uuid's user, if there are two same username in a group, only remove one of them
    def remove_user(self, msgId):
        if msgId in self.users:
            del self.users[msgId]

    def get_user_by_server_id(self, server_id):
        for key, value in self.users.items():
            if value[1] == server_id:
                return key
        return None

    def add_message(self, message):
        self.messages.append(message)

    def add_like(self, user, message_id):
        msgId = message_id - 1
        if msgId in range(len(self.messages)):
            message = self.messages[msgId]
        else:
            return False
        if user != message.user and user not in message.likes:
            message.likes.add(user)
            return True
        else:
            return False

    def remove_like(self, user, message_id):
        msgId = message_id - 1
        if msgId in range(len(self.messages)):
            message = self.messages[msgId]
        else:
            return False
        if user in message.likes:
            message.likes.remove(user)
            return True
        else:
            return False

# For every message, there is a message id, user who wrote it, message content and a set of data who liked it


class ChatMessage:
    def __init__(self, msgId, user, message):
        self.id = msgId
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
    temp = []
    for ele in log:
        temp.append([ele[0], MessageToJson(ele[1])])
    return temp


def log_decoder(json_list):
    log = []
    for element in json_list:
        grpc_msg = Parse(element[1], group_chat_pb2.ChatInput())
        log.append([element[0], grpc_msg])
    return log


class ChatServer(group_chat_pb2_grpc.ChatServerServicer):
    # Initialization.
    def __init__(self, server_address, server_id):
        self.users = {}
        self.groups = {}
        self.lastId = {}

        self.id = server_id
        self.vector = [0] * len(server_address)
        self.log = []
        self.queue = [HoldBackQueue()]*len(server_address)

        self.peers_address = {
            _id: server_address[_id] for _id in server_address.keys() if _id != self.id}
        self.stubs = {}
        self.channels = {}

        self.lock = threading.Lock()

        self.decodeFromFile()
    
    def getStub(self, server_id):
        if server_id in self.channels:
            return self.stubs[server_id]
        self.channels[server_id] = grpc.insecure_channel(self.peers_address[server_id])
        self.stubs[server_id] = group_chat_pb2_grpc.ChatServerStub(self.channels[server_id])
        return self.stubs[server_id]

    def removeStub(self, server_id):
        if server_id in self.channels:
            del self.channels[server_id]
        if server_id in self.stubs:
            del self.stubs[server_id]

    def chatFunction(self, request, context):
        # type 1: login, 2: join, 3: chat, 4: like, 5: dislike, 6: history, 7: quit
        try:
            uuid = []
            request.serverId = self.id
            with self.lock:
                response = self.processClientRequest(request)
            if response.status == "success":
                with self.lock:
                    self.vector[self.id-1] += 1
                    self.log.append([self.vector[:], request])
                    self.saveToDisk()
                deleteList = []
                for server_id in self.peers_address.keys():
                    try:
                        stub = self.getStub(server_id)
                        reqForSync = group_chat_pb2.ChatServerSyncRequest(
                            vector=self.vector, server_id=self.id)
                        response_from_server = stub.syncMessage(
                            reqForSync, timeout=1)
                    except Exception as e:
                        print("server: ", server_id)
                        if request.uuid in self.users and self.users[request.uuid] in self.groups:
                            tmp = self.groups[self.users[request.uuid]].get_user_by_server_id(server_id)
                            if tmp != None:
                                uuid.append(tmp)
                        deleteList.append(server_id)
                        print("error")
                        printLog(e)
                        continue
                req = group_chat_pb2.ChatServerRequest(vector=self.vector,
                                                       request=request, server_id=self.id, mode=1)
                for server_id in self.peers_address.keys():
                    try:
                        stub = self.getStub(server_id)
                        response_from_server = stub.sendMessage(
                            req, timeout=TIME_OUT)
                    except Exception as e:
                        deleteList.append(server_id)
                        printLog(e)
                        continue
                for server_id in deleteList:
                    self.removeStub(server_id)
            if len(uuid) > 0:
                print("exit")
                print(uuid)
                for item in uuid:
                    request = group_chat_pb2.ChatInput(
                            type=7, message="", userName="", groupName="", messageId=0, uuid=item)
                    self.chatFunction(request, context)
        except Exception as e:
            print("Chat function error")
            printLog(e)
        return response

    def syncMessage(self, request, context):
        r_vt = request.vector
        sender_id = request.server_id
        value = isConcurrent(r_vt, self.vector)
        print()
        print("Sync!!!!")
        print(r_vt)
        print(value)
        if value != 'greater':
            with self.lock:
                for i in reversed(self.log):
                    vector = i[0]
                    req = i[1]
                    if (req == None):
                        continue
                    temp = isConcurrent(vector, r_vt)
                    print()
                    print(vector)
                    print(temp)
                    print()
                    if temp == 'smaller':
                        break
                    try:
                        self.getStub(sender_id).sendMessage(group_chat_pb2.ChatServerRequest(
                            vector=vector, request=req, server_id=self.id, mode=0), timeout=TIME_OUT)
                    except Exception as e:
                        print("error")
                        print(e)
                        printLog(e)
        return group_chat_pb2.ChatServerResponse(status="success")

    def sendMessage(self, request, context):
        r_vt = request.vector
        req = request.request
        sender_id = request.server_id
        mode = request.mode
        print()
        print("receive")
        try:
            with self.lock:
                # if the request.vector[sender_id-1] is greater than self.vector[sender_id-1] + 1,
                # and other timestamp is at least as large as self.vector, then update
                # else put the request into the queue
                if r_vt[sender_id - 1] == self.vector[sender_id-1] + 1 and all(r_vt[k] >= self.vector[k] for k in range(len(self.vector)) if k != sender_id-1):
                    print("OK")
                    print()
                    self.vector[sender_id - 1] += 1
                    self.log.append([self.vector[:], req])
                    self.processClientRequest(req)
                    self.saveToDisk()
                else:
                    value = isConcurrent(r_vt, self.vector)
                    print("NOT OK ", value)
                    print()
                    if value == "greater" or value == "concurrent":
                        self.queue[sender_id-1].push(r_vt, req)
                while not self.queue[sender_id-1].isEmpty():
                    pos = self.getPosition(self.queue[sender_id-1].front()[0])
                    print(self.queue[sender_id-1].front()[1])
                    print("CACHE ", pos)
                    print("CACHE ", self.compareVector(self.queue[sender_id-1].front()[0]))
                    print()
                    #apply next message
                    if pos != -1:
                        req = self.queue[sender_id - 1].pop()[1]
                        self.vector[pos] += 1
                        self.log.append([self.vector[:], req])
                        self.processClientRequest(req)
                        self.saveToDisk()
                    #ignore messages with smaller vector 
                    elif self.compareVector(self.queue[sender_id-1].front()[0]) <= 0:
                        self.queue[sender_id-1].pop()
                    else:
                        break
                if mode == 1 and not self.queue[sender_id-1].isEmpty() and self.compareVector(self.queue[sender_id-1].front()[0]) > 1:
                    #have messages that bigger than self.vector at least 2, do sync
                    try:
                        tmpId = sender_id - 1
                        if sender_id > self.id:
                            tmpId -= 1
                        self.queue[sender_id-1].clear()
                        reqForSync = group_chat_pb2.ChatServerSyncRequest(
                            vector=self.vector, server_id=self.id)
                        response_from_server = self.getStub(tmpId).syncMessage(
                            reqForSync, timeout=1)
                    except Exception as e:
                        printLog(e)

        except Exception as e:
            print("Send message error")
            printLog(e)
        return group_chat_pb2.ChatServerResponse(status="success")

    def compareVector(self, v):
        result = 0
        index = -1
        for item in v:
            index += 1
            if index == self.id - 1:
                continue
            result += item - self.vector[index]
        return result

    def getPosition(self, v):
        result = 0
        index = -1
        pos = -1
        for item in v:
            index += 1
            if index == self.id - 1:
                continue
            tmp = item - self.vector[index]
            if tmp == 1:
                pos = index
            result += tmp
        if result == 1:
            return pos
        else:
            return -1

    def prope(self, request, context):
        return group_chat_pb2.Empty()

    def processClientRequest(self, request):
        try:
            _type = request.type
            if _type == 1:
                # if the user joined another group, we need to remove it from that group
                if request.uuid in self.users and self.users[request.uuid] in self.groups:
                    self.groups[self.users[request.uuid]
                                ].remove_user(request.uuid)
                return group_chat_pb2.ChatOutput(status="success", messages=[])
            elif _type == 2:
                # if the user joined another group, we need to remove it from that group
                if request.uuid in self.users and self.users[request.uuid] in self.groups:
                    self.groups[self.users[request.uuid]].remove_user(request.uuid)
                if request.groupName not in self.groups.keys():
                    self.groups[request.groupName] = ChatRoom(
                        request.groupName)
                self.groups[request.groupName].add_user(request.userName, request.uuid, request.serverId)
                self.users[request.uuid] = request.groupName
                participantsSet = set()
                tmpUsers = self.groups[request.groupName].users.copy()
                for value in tmpUsers.values():
                    participantsSet.add(value[0])
                return group_chat_pb2.ChatOutput(status="success", messages=[], user=list(participantsSet))
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
                views = [group_chat_pb2.ChatMessage(content=str(self.id))]
                deleteList = []
                for server_id in self.peers_address.keys():
                    try:
                        stub = self.getStub(server_id)
                        stub.probe(group_chat_pb2.Empty())
                        views.append(
                            group_chat_pb2.ChatMessage(content=str(server_id)))
                    except grpc.RpcError as e:
                        deleteList.append(server_id)
                        continue
                for server_id in deleteList:
                    self.removeStub(server_id)
                return group_chat_pb2.ChatOutput(status="success", messages=views)
            else:
                return group_chat_pb2.ChatOutput(status="failed", messages=[])
        except ValueError:
            printLog("Error type")

    def getMessages(self, request, context):
        if request.uuid not in self.lastId.keys():
            self.lastId[request.uuid] = 0
        participantsSet = set()
        tmpUsers = self.groups[request.groupName].users.copy()
        for value in tmpUsers.values():
            participantsSet.add(value[0])
        lastParticipants = len(list(participantsSet))
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
            participantsSet = set()
            tmpUsers = self.groups[request.groupName].users.copy()
            for value in tmpUsers.values():
                participantsSet.add(value[0])
            participants = list(participantsSet)
            if (lastParticipants != len(participants)):
                lastParticipants = len(participants)
                yield group_chat_pb2.ChatMessage(id=-998, user=", ".join(participants), content=request.groupName, numberOfLikes=0)
            if len(chatRoom.messages) > lastId:
                self.lastId[request.uuid] = len(chatRoom.messages)
                for message in chatRoom.messages[-10:]:
                    yield group_chat_pb2.ChatMessage(id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes))

    def probe(self, request, context):
        return group_chat_pb2.Empty()

    def decodeFromFile(self):
        server_id = self.id
        if (isfile(f'./logs/log_{server_id}.json')):
            with open(f'./logs/log_{server_id}.json', 'r') as fp:
                self.log = log_decoder(json.load(fp))
        for log in self.log:
            with self.lock:
                self.processClientRequest(log[1])
                self.vector = log[0][:]

    def saveToDisk(self):
        printLog("Writing...")
        with open(f'./logs/log_{self.id}.json', 'w') as f:
            json.dump(log_encoder(self.log), f, indent=4)


def start_server():
    global DEBUG
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Server id")
    parser.add_argument("-D", help="Debug", action="store_true")
    args = parser.parse_args()
    if args.id is None:
        print(
            "Please specify server id with command : python server.py -id [id]")
        sys.exit(1)
    if args.D:
        DEBUG = True
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
    server_id = int(args.id)
    chatServer = ChatServer(server_address, server_id)
    server = grpc.server(futures.ThreadPoolExecutor())
    group_chat_pb2_grpc.add_ChatServerServicer_to_server(chatServer, server)
    host, port = server_address[server_id].split(":")
    print(f"Server started on {host}:{port}! ")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    server.wait_for_termination()


def printLog(msg):
    global DEBUG
    if False:
        logger.exception(str(msg))


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
