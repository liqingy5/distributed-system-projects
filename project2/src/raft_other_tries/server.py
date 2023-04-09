from atexit import register
from concurrent import futures
from os.path import isfile
from math import ceil
from random import random,uniform
from time import time, sleep
import enum
import grpc
import sys
import raft_pb2
import raft_pb2_grpc

class Role(enum.Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

# Timeout for election.
def election_timeout():
    return time()+uniform(1, 3)
# Timeout for heartbeat.
def heartbeat_timeout():
    return time()+0.5

#MRAFT server.
class RaftServer(raft_pb2_grpc.RaftServerServicer):
    #Initialization.   
    def __init__(self, server_address,server_id):
        self.role = Role.FOLLOWER
        print(f"Server {server_id} is a follower")
        self.last_log_idx = 0
        self.last_log_term = 0
        self.commit_idx = 0
        self.id = server_id
        self.leader_id = None
        self.log = {}
        self.peers_address = {_id:server_address[_id] for _id in server_address.keys() if _id != self.id}
        self.term = 0
        self.timeout = election_timeout()
        self.vote_count = 0
        self.voted_for = -1
        self.stubs = {_id:raft_pb2_grpc.RaftServerStub(grpc.insecure_channel(server_address[_id])) for _id in server_address.keys() if _id != self.id}
        if (isfile(f'log_{server_id}.txt')):
            with open(f'log_{server_id}.txt', 'r') as fp:
                line = fp.readline()
                while (line):
                    temp = line.strip('\n').split(' ')
                    entry = raft_pb2.Entry(term=int(temp[0]), index=int(temp[1]), decree=temp[2])
                    self.log[entry.index] = entry
                    self.last_log_idx = entry.index
                    self.last_log_term = entry.term
                    line = fp.readline()

#Function to Update my state once in a while. 
    def update(self):
        if (self.role == Role.FOLLOWER):
            if (time() > self.timeout):
                self.role = Role.CANDIDATE
                print(f"Server {self.id} is a candidate")
        elif (self.role == Role.CANDIDATE):
            if (time() > self.timeout):
                self.term += 1
                self.vote_count = 1
                #Requesting Vote.
                print(f"Server {self.id} is requesting vote")
                req = raft_pb2.RequestVoteRequest(term=self.term, cadidateId=self.id, lastLogIndex=self.last_log_idx,
                                                  lastLogTerm=self.last_log_term)
                for id in self.stubs.keys():
                    stub = self.stubs[id]
                    try:
                        #Store Response.
                        response = stub.RequestVote(req)
                        print('Got request vote response: {}'.format(response))
                        if (response.voteGranted):
                            self.vote_count += 1
                    except:
                        print('cannot connect to ' + str(self.peers_address[id]))
                self.timeout = election_timeout()
            elif (self.vote_count >= (len(self.peers_address) + 1) // 2 + 1):
                self.role = Role.LEADER
                self.vote_count = 1
                self.voted_for = self.id
                self.timeout = time()
                print('Now I am the Leader!!!')
        elif (self.role == Role.LEADER):
            if (time() > self.timeout):
                prevLogIndex = self.last_log_idx
                if (prevLogIndex in self.log):
                    entry = self.log[prevLogIndex]
                else:
                    entry = None
                #Append Entries Request.
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
                            #Append Entries Request.
                            print('Sending Append entries request...')
                            req = raft_pb2.AppendEntriesRequest(term=self.term,leaderId=self.id,
                                                                prevLogIndex=prevLogIndex, prevLogTerm=entry.term,
                                                                entry=entry, leaderCommit=self.commit_idx)
                            response = stub.AppendEntries(req)
                            print('I am the Leader!!!')
                            print('Got append entries response: {}'.format(response))
                        while (prevLogIndex < self.last_log_idx):
                            prevLogIndex += 1
                            entry = self.log[prevLogIndex]
                            print('Sending Append entries request...')
                            #Append Entries Request.
                            req = raft_pb2.AppendEntriesRequest(term=self.term, leaderId=self.id,
                                                                prevLogIndex=prevLogIndex, prevLogTerm=entry.term,
                                                                entry=entry, leaderCommit=self.commit_idx)
                            response = stub.AppendEntries(req)
                            print('I am the Leader!!!')
                            print('Got append entries response: {}'.format(response))
                    except:
                        print('cannot connect to ' + str(self.peers_address[id]))
                self.timeout = heartbeat_timeout()

#Function to Request Vote.
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

#Function to handle Append Entries.
    def AppendEntries(self, req, context):
        print('Got append entries: {}'.format(req))
        if (req.term < self.term or (
                req.prevLogIndex in self.log and self.log[req.prevLogIndex].term != req.prevLogTerm)):
            print('Returning Append entries Response as false since requested term is less')  
            return raft_pb2.AppendEntriesResponse(term=self.term, success=False)
        self.role = Role.FOLLOWER
        print('I am a follower!!!')
        self.term = req.term
        self.leader_id = req.leaderId
        self.timeout = election_timeout()
        if (req.prevLogIndex == self.last_log_idx + 1 and req.prevLogTerm >= self.last_log_term):
            self.log[req.entry.index] = req.entry
            self.last_log_idx += 1
            self.last_log_term = req.prevLogTerm
            print(self.log)
            print('Returning Append entries Response as True')
            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        if (req.prevLogIndex == self.last_log_idx and req.prevLogTerm == self.last_log_term):
            print('Returning Append entries Response as True')
            return raft_pb2.AppendEntriesResponse(term=self.term, success=True)
        print('Returning Append entries Response as false')
        return raft_pb2.AppendEntriesResponse(term=self.term, success=False)

#Function to handle Client Append Request.
    def ClientAppend(self, req, context):
        print('Got client append: {}'.format(req))
        if (self.role != Role.LEADER):
            print('Returning Client append Response as rc = 1 since I am not a leader')
            return raft_pb2.ClientAppendResponse(rc=1, leader=self.leader_id, index=self.last_log_idx)
        self.last_log_term = self.term
        self.last_log_idx += 1
        entry = raft_pb2.Entry(term=self.term, index=self.last_log_idx, decree=req.decree)
        self.log[self.last_log_idx] = entry
        #Append Entries Request.
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
        self.commit_idx += 1
        self.timeout = heartbeat_timeout()
        print('Returning Client append Response as rc = 0')
        return raft_pb2.ClientAppendResponse(rc=0, leader=self.id, index=self.last_log_idx)

#Function to handle client request index.
    def ClientRequestIndex(self, req, context):
        print('Got client request index: {}'.format(req))
        if (req.index in self.log):
            print('Returning Client request index Response as rc = 0')
            return raft_pb2.ClientRequestIndexResponse(rc=0, leader=self.leader_id, index=req.index,
                                                       decree=self.log[req.index].decree)
        if (self.role != Role.LEADER):
            print('Returning Client request index Response as rc = 1 since I am not a leader')
            return raft_pb2.ClientRequestIndexResponse(rc=1, leader=self.leader_id, index=req.index, decree=None)
        print('Returning Client request index Response as rc = 0')
        return raft_pb2.ClientRequestIndexResponse(rc=0, leader=self.leader_id, index=req.index, decree=None)  
#Storing Log Information.
    def get_log(self):
        return self.log

#Function to save to disk.
def saveToDisk():
    print("Writing...")
    with open(f'log_{sys.argv[1]}.txt', 'w') as f:
        log = raftserver.get_log()
        for entry in log.values():
            f.write(str(entry.term) + ' ' + str(entry.index) + ' ' + entry.decree + '\n')
#Calling the save to disk function.
register(saveToDisk)

#Read the text file and store replica_number and address:Port as (key,value) pair in a Dictionary.
if __name__ == '__main__':
    server_address = {}
    with open( './config.txt', 'r') as f:
        line = f.readline()
        while (line):
            id,addr = line.split()
            server_address[int(id)] = addr
            line = f.readline()
    print(server_address)

    #Calling the Raft_server class.
    server_id = int(sys.argv[1])
    raftserver = RaftServer(server_address, server_id)
    server = grpc.server(futures.ThreadPoolExecutor())
    raft_pb2_grpc.add_RaftServerServicer_to_server(raftserver, server)
    #Set default IP address and Port number is taken as argument.
    host, port = server_address[server_id].split(":")
    server.add_insecure_port(f"{host}:{port}")
    #Start the server.
    server.start()
    while True:
        try:
            sleep(0.1)
            raftserver.update()
        except KeyboardInterrupt:
            server.stop(0)