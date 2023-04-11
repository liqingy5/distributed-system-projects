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
import raft_pb2
import raft_pb2_grpc
import threading
import asyncio
import json
import argparse

DEBUG = True


class Role(enum.Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

# Timeout for election.


def election_timeout():
    return time()+uniform(0.6, 0.9)
# Timeout for heartbeat.


def heartbeat_timeout():
    return time()+0.3

# Chat room class to store information about a chat room


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
        grpc_msg = Parse(json_dict[key], raft_pb2.Entry())
        log[int(key)] = grpc_msg
    return log


class RaftServer(raft_pb2_grpc.RaftServerServicer):
    # Initialization.
    def __init__(self, server_address, server_id):
        self.users = {}
        self.groups = {}
        self.lastId = {}

        self.role = Role.FOLLOWER
        print(f"Server {server_id} is a follower")
        self.last_log_idx = 0
        self.last_log_term = 0
        self.commit_idx = 0
        self.id = server_id
        self.leader_id = None
        self.log = {}
        self.peers_address = {
            _id: server_address[_id] for _id in server_address.keys() if _id != self.id}
        self.term = 0
        self.timeout = election_timeout()
        self.vote_count = 0
        self.voted_for = -1
        self.stubs = {_id: raft_pb2_grpc.RaftServerStub(grpc.insecure_channel(
            server_address[_id])) for _id in server_address.keys() if _id != self.id}

        self.decodeFromFile()

    def decodeFromFile(self):
        server_id = self.id
        if (isfile(f'log_{server_id}.json')):
            with open(f'log_{server_id}.json', 'r') as fp:
                self.log = log_decoder(json.load(fp))
                print("Decode log success")

        if (isfile(f'groups_{server_id}.json')):
            with open(f'groups_{server_id}.json', 'r') as fp:
                self.groups = groups_decoder(json.load(fp))

        if (isfile(f'users_{server_id}.json')):
            with open(f'users_{server_id}.json', 'r') as fp:
                self.users = json.load(fp)
        if (isfile(f'lastId_{server_id}.json')):
            with open(f'lastId_{server_id}.json', 'r') as fp:
                self.lastId = json.load(fp)

        if (isfile(f'state_{server_id}.json')):
            with open(f'state_{server_id}.json', 'r') as fp:
                data = json.load(fp)
                self.term = data['term']
                self.voted_for = data['voted_for']
                self.commit_idx = data['commit_idx']
                self.last_log_idx = data['last_log_idx']
                self.last_log_term = data['last_log_term']

    # Function to Update my state once in a while.
    def update(self):
        if (self.role == Role.FOLLOWER):
            if (time() > self.timeout):
                self.role = Role.CANDIDATE
                print(f"Server {self.id} is a candidate")
        elif (self.role == Role.CANDIDATE):
            if (time() > self.timeout):
                self.term += 1
                self.vote_count = 1
                self.voted_for = self.id
                # Requesting Vote.
                print(f"Server {self.id} is requesting vote")
                req = raft_pb2.RequestVoteRequest(term=self.term, candidateId=self.id, lastLogIndex=self.last_log_idx,
                                                  lastLogTerm=self.last_log_term)
                for id in self.stubs.keys():
                    stub = self.stubs[id]
                    try:
                        # Store Response.
                        response = stub.RequestVote(req)
                        print('Got request vote response: {}'.format(response))
                        if (response.voteGranted):
                            self.vote_count += 1
                    except grpc.RpcError as e:
                        print('cannot connect to ' +
                              str(self.peers_address[id]))
                        print(e)
                self.timeout = election_timeout()
            elif (self.vote_count >= (len(self.peers_address) + 1) // 2 + 1):
                self.role = Role.LEADER
                self.vote_count = 1
                self.voted_for = -1
                self.leader_id = self.id
                self.timeout = time()
                print('Now I am the Leader!!!')
        elif (self.role == Role.LEADER):
            if (time() > self.timeout):
                prevLogIndex = self.last_log_idx
                if (prevLogIndex in self.log):
                    entry = self.log[prevLogIndex]
                else:
                    entry = None
                # Append Entries Request.
                req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id, prevLogIndex=prevLogIndex,
                                                    prevLogTerm=self.last_log_term, entry=entry,
                                                    leaderCommit=self.commit_idx)
                print('Sending Append entries request...')
                for id in self.stubs.keys():
                    stub = self.stubs[id]
                    try:
                        response = stub.AppendEntries(req)
                        print('I am the Leader!!!')
                        print('Got append entries response: {}'.format(response))
                        while (response.success == False):
                            if (prevLogIndex > 1):
                                prevLogIndex -= 1
                            entry = self.log[prevLogIndex]
                            # Append Entries Request.
                            print(
                                f'Sending Append entries request to server {id} with {entry}')
                            req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id,
                                                                prevLogIndex=prevLogIndex, prevLogTerm=entry.term,
                                                                entry=entry, leaderCommit=self.commit_idx)
                            response = stub.AppendEntries(req)
                            print('I am the Leader!!!')
                            print('Got append entries response: {}'.format(response))
                        while (prevLogIndex < self.last_log_idx):
                            prevLogIndex += 1
                            entry = self.log[prevLogIndex]
                            print('Sending Append entries request...')
                            # Append Entries Request.
                            req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id,
                                                                prevLogIndex=prevLogIndex, prevLogTerm=entry.term,
                                                                entry=entry, leaderCommit=self.commit_idx)
                            response = stub.AppendEntries(req)
                            print('I am the Leader!!!')
                            print('Got append entries response: {}'.format(response))
                    except grpc.RpcError as e:
                        print('cannot connect to ' +
                              str(self.peers_address[id]))
                        print(e)
                self.timeout = heartbeat_timeout()

    # Function to Request Vote.
    def RequestVote(self, req, context):
        print('Got request vote: {}'.format(req))
        if (req.term > self.term):
            self.term = req.term
            self.voted_for = -1
        if (req.term < self.term) or (req.term == self.term and self.voted_for != -1 and self.voted_for != req.candidateId and self.last_log_idx > req.prevLogIndex):
            print('Returning Vote Response as false since requested term is less')
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)
        if ((self.voted_for == -1 or self.voted_for == req.candidateId) and (req.lastLogTerm > self.last_log_term or (
                req.lastLogTerm == self.last_log_term and req.lastLogIndex >= self.last_log_idx))):
            self.role = Role.FOLLOWER
            print('I am a Follower!!!')
            self.voted_for = req.candidateId
            self.timeout = election_timeout()
            print('Returning Vote Response : granted vote')
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=True)
        print('Returning Vote Response as False')
        return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)

    # Function to handle Append Entries.
    def AppendEntries(self, req, context):
        print('Got append entries: {}'.format(req))
        if (req.term < self.term or (
                req.prevLogIndex in self.log and self.log[req.prevLogIndex].term != req.prevLogTerm)):
            print(
                'Returning Append entries Response as false since requested term is less')
            return raft_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.role = Role.FOLLOWER
        print('I am a follower!!!')
        self.term = req.term
        self.leader_id = req.leaderId
        self.timeout = election_timeout()
        if (req.prevLogIndex == self.last_log_idx and req.prevLogTerm == self.last_log_term):
            print('Returning Append entries Response as True')
            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        elif (req.prevLogIndex == self.last_log_idx+1 and req.prevLogTerm >= self.last_log_term):
            print(
                f"Receive entry from leader: {req.leaderId} ,index: {req.prevLogIndex} prevLogTerm:{req.prevLogTerm} with Entry:{req.entry} ")
            self.log[req.entry.index] = req.entry
            self.last_log_idx += 1
            self.last_log_term = req.prevLogTerm
            self.processClientRequest(req.entry.request)
            self.commit_idx += 1
            print('Returning Append entries Response as True')
            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        print('Returning Append entries Response as false')
        return raft_pb2.AppendEntriesResponse(term=self.term, success=False)

    def chatFunction(self, request, context):
        # type 1: login, 2: join, 3: chat, 4: like, 5: dislike, 6: history
        if (self.role != Role.LEADER):
            print(
                'Returning Client chat response with status as failed since I am not a leader')
            return raft_pb2.ChatOutput(status="failed", messages=[])
        print('Request from Client: {}'.format(request))
        self.last_log_term = self.term
        self.last_log_idx += 1
        entry = raft_pb2.Entry(
            term=self.term, index=self.last_log_idx, request=request)
        self.log[self.last_log_idx] = entry
        print(
            f"Entry: {entry.term}, {entry.index}, {entry.request.type}, {entry.request.message}")
        print('Sending Append entries Request...')
        req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id, prevLogIndex=self.last_log_idx,
                                            prevLogTerm=self.last_log_term, entry=entry, leaderCommit=self.commit_idx)

        for id in self.stubs.keys():
            stub = self.stubs[id]
            try:
                response = stub.AppendEntries(req)
                print('I am the Leader!!!')
                print('Got append entries response: {}'.format(response))
            except grpc.RpcError as e:
                print('cannot connect to ' +
                      str(self.peers_address[id]))
                print(e)

        response = self.processClientRequest(request)
        self.commit_idx += 1
        self.timeout = heartbeat_timeout()
        print('Returning Client chat response with status as success')
        print(response)
        return response

    def processClientRequest(self, request):
        try:
            _type = request.type
            if _type == 1:
                return raft_pb2.ChatOutput(status="success", messages=[])
            elif _type == 2:
                # if the user joined another group, we need to remove it from that group
                if request.uuid in self.users and self.users[request.uuid] in self.groups:
                    self.groups[self.users[request.uuid]
                                ].remove_user(request.uuid)
                if request.groupName not in self.groups.keys():
                    self.groups[request.groupName] = ChatRoom(
                        request.groupName)
                self.groups[request.groupName].add_user(
                    request.userName, request.uuid)
                self.users[request.uuid] = request.groupName
                return raft_pb2.ChatOutput(status="success", messages=[], user=list(set(self.groups[request.groupName].users.values())))
            elif _type == 3:
                chatRoom = self.groups[request.groupName]
                chatRoom.add_message(ChatMessage(
                    len(chatRoom.messages) + 1, request.userName, request.message))
                return raft_pb2.ChatOutput(status="success", messages=[])
            elif _type == 4:
                chatRoom = self.groups[request.groupName]
                if not chatRoom.add_like(request.userName, request.messageId):
                    return raft_pb2.ChatOutput(status="success", messages=[])
                # only when the message user liked is within lastest 10 message, we need to refresh the message list
                if request.messageId > len(chatRoom.messages) - 10:
                    for element in self.lastId:
                        if self.lastId[element] > 0:
                            self.lastId[element] = self.lastId[element] - 1
                return raft_pb2.ChatOutput(status="success", messages=[])
            elif _type == 5:
                chatRoom = self.groups[request.groupName]
                if not chatRoom.remove_like(request.userName, request.messageId):
                    return raft_pb2.ChatOutput(status="success", messages=[])
                if request.messageId > len(chatRoom.messages) - 10:
                    for element in self.lastId:
                        if self.lastId[element] > 0:
                            self.lastId[element] = self.lastId[element] - 1
                return raft_pb2.ChatOutput(status="success", messages=[])
            elif _type == 6:
                chatRoom = self.groups[request.groupName]
                message = chatRoom.messages
                msg_list = []
                for message in chatRoom.messages:
                    msg_list.append(raft_pb2.ChatMessage(
                        id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes)))
                return raft_pb2.ChatOutput(status="success", messages=msg_list)
            elif _type == 7:
                self.groups[request.groupName].remove_user(request.uuid)
                return raft_pb2.ChatOutput(status="success", messages=[])
            elif _type == 8:
                return raft_pb2.ChatOutput(status="success", messages=[raft_pb2.ChatMessage(content=str(self.leader_id))])
            else:
                return raft_pb2.ChatOutput(status="failed", messages=[])
        except ValueError:
            print("Error type")

    def getMessages(self, request, context):
        self.lastId[request.uuid] = 0
        lastParticipants = len(
            list(set(self.groups[request.groupName].users.values())))
        while (True):
            # if the user has joined another group, remove it
            if request.uuid not in self.groups[request.groupName].users.keys():
                yield raft_pb2.ChatMessage(id=-999, user="", content="", numberOfLikes=0)
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
                yield raft_pb2.ChatMessage(id=-998, user=", ".join(participants), content=request.groupName, numberOfLikes=0)
            if len(chatRoom.messages) > lastId:
                self.lastId[request.uuid] = len(chatRoom.messages)
                for message in chatRoom.messages[-10:]:
                    yield raft_pb2.ChatMessage(id=message.id, user=message.user, content=message.message, numberOfLikes=len(message.likes))


def saveToDisk(server_id, raftserver):
    print("Writing...")
    with open(f'log_{server_id}.json', 'w') as f:
        json.dump(log_encoder(raftserver.log), f, indent=4)
    with open(f'state_{server_id}.json', 'w') as f:
        persistant_state = {"term": raftserver.term,
                            "voted_for": raftserver.voted_for, "commit_idx": raftserver.commit_idx, "last_log_idx": raftserver.last_log_idx, "last_log_term": raftserver.last_log_term}
        json.dump(persistant_state, f)
    with open(f'groups_{server_id}.json', 'w') as f:
        json.dump(raftserver.groups, f, indent=4, cls=ChatRoomEncoder)

    with open(f'users_{server_id}.json', 'w') as f:
        json.dump(raftserver.users, f)

    with open(f'lastId_{server_id}.json', 'w') as f:
        json.dump(raftserver.lastId, f)


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
    print(server_address)
    parser = argparse.ArgumentParser()
    parser.add_argument("-id", help="Server id")
    args = parser.parse_args()
    if args.id is None:
        print(
            "Please specify server id with command : python server.py -id [id]")
        sys.exit(1)
    server_id = int(args.id)
    raftserver = RaftServer(server_address, server_id)
    server = grpc.server(futures.ThreadPoolExecutor())
    raft_pb2_grpc.add_RaftServerServicer_to_server(raftserver, server)
    host, port = server_address[server_id].split(":")
    print(f"Server started on port {port}! ")
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    register(saveToDisk, server_id, raftserver)

    while True:
        try:
            raftserver.update()
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    # Start the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
