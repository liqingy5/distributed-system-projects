from atexit import register
from concurrent import futures
from os.path import isfile
from math import ceil
from random import random, uniform
from time import time, sleep
import enum
import grpc
import sys
import raft_pb2
import raft_pb2_grpc
import threading
import asyncio
import json


class Role(enum.Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

# Timeout for election.


def election_timeout():
    return time()+uniform(11, 13)
# Timeout for heartbeat.


def heartbeat_timeout():
    return time()+5

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
        if (isfile(f'log_{server_id}.txt')):
            with open(f'log_{server_id}.txt', 'r') as fp:
                line = fp.readline()
                while (line):
                    temp = line.strip('\n').split(' ')
                    entry = raft_pb2.Entry(
                        term=int(temp[0]), index=int(temp[1]), type=int(temp[2]), value=temp[3])
                    self.log[entry.index] = entry
                    self.last_log_idx = entry.index
                    self.last_log_term = entry.term
                    line = fp.readline()

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
                req = raft_pb2.RequestVoteRequest(term=self.term, cadidateId=self.id, lastLogIndex=self.last_log_idx,
                                                  lastLogTerm=self.last_log_term)
                for id in self.stubs.keys():
                    stub = self.stubs[id]
                    try:
                        # Store Response.
                        response = stub.RequestVote(req)
                        print('Got request vote response: {}'.format(response))
                        if (response.voteGranted):
                            self.vote_count += 1
                    except:
                        print('cannot connect to ' +
                              str(self.peers_address[id]))
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
                            prevLogIndex -= 1
                            entry = self.log[prevLogIndex]
                            # Append Entries Request.
                            print('Sending Append entries request...')
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
                    except:
                        print('cannot connect to ' +
                              str(self.peers_address[id]))
                self.timeout = heartbeat_timeout()

    # Function to Request Vote.
    def RequestVote(self, req, context):
        print('Got request vote: {}'.format(req))
        if (req.term > self.term):
            self.term = req.term
            self.voted_for = -1
        if (req.term < self.term):
            print('Returning Vote Response as false since requested term is less')
            return raft_pb2.RequestVoteResponse(term=self.term, voteGranted=False)
        if ((self.voted_for == -1 or self.voted_for == req.cadidateId) and (req.lastLogTerm > self.last_log_term or (
                req.lastLogTerm == self.last_log_term and req.lastLogIndex >= self.last_log_idx))):
            self.role = Role.FOLLOWER
            print('I am a Follower!!!')
            self.voted_for = req.cadidateId
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
        if (req.prevLogIndex >= self.last_log_idx and req.prevLogTerm >= self.last_log_term):
            if (req.prevLogIndex == self.last_log_idx and req.prevLogTerm == self.last_log_term):
                print('Returning Append entries Response as True')
            else:
                self.log[req.entry.index] = req.entry
                self.last_log_idx += 1
                self.last_log_term = req.prevLogTerm
                print(self.log)
                print('Returning Append entries Response as True')
            if (req.leaderCommit > self.commit_idx):
                new_commit_idx = min(req.leaderCommit, self.last_log_idx)
                while new_commit_idx > self.commit_idx:
                    self.commit_idx += 1
                    self.processClientRequest(self.log[self.commit_idx])

            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        print('Returning Append entries Response as false')
        return raft_pb2.AppendEntriesResponse(term=self.term, success=False)

    # # Function to handle Client Append Request.
    # def ClientAppend(self, req, context):
    #     print('Got client append: {}'.format(req))
    #     if (self.role != Role.LEADER):
    #         print('Returning Client append Response as rc = 1 since I am not a leader')
    #         return raft_pb2.ClientAppendResponse(rc=1, leader=self.leader_id, index=self.last_log_idx)
    #     self.last_log_term = self.term
    #     self.last_log_idx += 1
    #     entry = raft_pb2.Entry(
    #         term=self.term, index=self.last_log_idx, decree=req.decree)
    #     self.log[self.last_log_idx] = entry
    #     # Append Entries Request.
    #     print('Sending Append entries Request...')
    #     req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id, prevLogIndex=self.last_log_idx,
    #                                         prevLogTerm=self.last_log_term, entry=entry, leaderCommit=self.commit_idx)
    #     for id in self.stubs.keys():
    #         stub = self.stubs[id]
    #         try:
    #             response = stub.AppendEntries(req)
    #             print('I am the Leader!!!')
    #             print('Got append entries response: {}'.format(response))
    #         except:
    #             print('cannot connect to ' + str(self.peers_address[id]))
    #     self.commit_idx += 1
    #     self.timeout = heartbeat_timeout()
    #     print('Returning Client append Response as rc = 0')
    #     return raft_pb2.ClientAppendResponse(rc=0, leader=self.id, index=self.last_log_idx)

    # # Function to handle client request index.
    # def ClientRequestIndex(self, req, context):
    #     print('Got client request index: {}'.format(req))
    #     if (req.index in self.log):
    #         print('Returning Client request index Response as rc = 0')
    #         return raft_pb2.ClientRequestIndexResponse(rc=0, leader=self.leader_id, index=req.index,
    #                                                    decree=self.log[req.index].decree)
    #     if (self.role != Role.LEADER):
    #         print(
    #             'Returning Client request index Response as rc = 1 since I am not a leader')
    #         return raft_pb2.ClientRequestIndexResponse(rc=1, leader=self.leader_id, index=req.index, decree=None)
    #     print('Returning Client request index Response as rc = 0')
    #     return raft_pb2.ClientRequestIndexResponse(rc=0, leader=self.leader_id, index=req.index, decree=None)

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
            term=self.term, index=self.last_log_idx, type=request.type, value=request.message)
        self.log[self.last_log_idx] = entry
        print(
            f"Entry: {entry.term}, {entry.index}, {entry.type}, {entry.value}")
        print('Sending Append entries Request...')
        req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id, prevLogIndex=self.last_log_idx,
                                            prevLogTerm=self.last_log_term, entry=entry, leaderCommit=self.commit_idx)

        for id in self.stubs.keys():
            stub = self.stubs[id]
            try:
                response = stub.AppendEntries(req)
                print('I am the Leader!!!')
                print('Got append entries response: {}'.format(response))
            except:
                print('cannot connect to ' + str(self.peers_address[id]))

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
    with open(f'log_{server_id}.txt', 'w') as f:
        log = raftserver.log
        for entry in log.values():
            f.write(str(entry.term) + ' ' + str(entry.index) +
                    ' ' + str(entry.type) + ' '+str(entry.value)+'\n')
    with open(f'state_{server_id}.json', 'w') as f:
        persistant_state = {"term": raftserver.term,
                            "voted_for": raftserver.voted_for, "commit_idx": raftserver.commit_idx}
        json.dump(persistant_state, f)
    with open(f'groups_{server_id}.json', 'w') as f:
        json.dump(raftserver.groups, f, indent=4, cls=ChatRoomEncoder)

    with open(f'users_{server_id}.json', 'w') as f:
        json.dump(raftserver.users, f)

    with open(f'lastId_{server_id}.json', 'w') as f:
        json.dump(raftserver.lastId, f)


def start_server():
    server_address = {}
    with open('./config.txt', 'r') as f:
        line = f.readline()
        while (line):
            id, addr = line.split()
            server_address[int(id)] = addr
            line = f.readline()
    print(server_address)

    server_id = int(sys.argv[1])
    raftserver = RaftServer(server_address, server_id)
    server = grpc.server(futures.ThreadPoolExecutor())
    raft_pb2_grpc.add_RaftServerServicer_to_server(raftserver, server)
    host, port = server_address[server_id].split(":")
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    register(saveToDisk, server_id, raftserver)

    while True:
        try:
            sleep(0.1)
            raftserver.update()
        except KeyboardInterrupt:
            server.stop(0)


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    print("Server started on port 8001! ")

    # Start the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()
