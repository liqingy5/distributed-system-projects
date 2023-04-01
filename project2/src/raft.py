## Just pseudocode for now, can change later
import asyncio
import grpc
import time
import json
import threading
import os.path
import raftMessage_pb2
import raftMessage_pb2_grpc
from concurrent import futures

election_timeout = 150 #ms
heartbeat_timeout = 100 #ms
class RaftNode(raftMessage_pb2_grpc.raftMessageServicer):
    def __init__(self, _id, meta):
        self.id = _id
        self.peers = {key:meta[key] for key in meta.keys() if _id!=key} ## dict of peers (e.g., {1:'localhost:50051', 2:'localhost:50052'})
        self.addr = meta['id'] ## address of this server (e.g., 'localhost:50051')
        self.channel = grpc.insecure_channel(self.addr) 
        self.stub = raftMessage_pb2_grpc.raftMessageStub(self.channel)
        self.state = 'candidate'
        # Persistent state on all servers:
        
        self.currentTerm = 0 ## latest term server has seen (initialized to 0 on first boot, increases monotonically)
        self.votedFor = None ## candidateId that received vote in current term (or null if none)
        self.loadPersistentState() ## load persistent state from file if exist
        
        self.logs = [] ## log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)
        self.loadLog() ## load log from file if exist

        # Volatile state on all servers:
        
        self.commitIndex = 0 ## index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.lastApplied = 0 ## index of highest log entry applied to state machine (initialized to 0, increases monotonically)
        
        # Volatile state on leaders:
        
        self.nextIndex = {} ## for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.matchIndex = {} ## for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)

        #Append Entries
        self.leaderId = None

        #Request Votes
        self.voteIds={id:0 for id in self.peers.keys() if id!=self.id}

        ## election timeout
        self.leader_selection_time = time.time() + election_timeout

        ## heartbeat timeout
        self.next_heartbeat_time = time.time() + heartbeat_timeout
    def __str__(self):
        return 'Raft(id={}, state={}, currentTerm={}, votedFor={}, log={}, commitIndex={}, lastApplied={}, nextIndex={}, matchIndex={})'.format(
            self.id, self.state, self.currentTerm, self.votedFor, self.log, self.commitIndex, self.lastApplied, self.nextIndex, self.matchIndex)
    
    def __repr__(self):
        return self.__str__()
    
    ## Log entries operations
    def saveLog(self):
        filename = './logs/log_{}.json'.format(self.id)
        with open(filename, 'w') as f:
            json.dump(self.log, f)
    def loadLog(self):
        filename = './logs/log_{}.json'.format(self.id)
        if not os.path.isfile(filename):
            self.saveLog()
        with open(filename, 'r') as f:
            self.log = json.load(f)
    def deleteEntry(self, index):
        if index<0 or index>=len(self.log):
            return
        self.log = self.log[:index]
        self.saveLog()
    def getLogTerm(self, index):
        if(index<0 or index>=len(self.log)):
            return -1
        return self.log[index].term
    def appendLogEntries(self, entry):
        self.log+=entry
        self.saveLog()
        return
    
    ## Persistent state operations
    def savePersistentState(self):
        persistent = {'currentTerm':self.currentTerm, 'votedFor':self.votedFor}
        filename = './states/persistent_state_{}.json'.format(self.id)
        with open(filename, 'w') as f:
            json.dump(persistent, f)
    def loadPersistentState(self):
        filename = './states/persistent_state_{}.json'.format(self.id)
        if not os.path.isfile(filename):
            self.savePersistentState()
        with open(filename, 'r') as f:
            persistent = json.load(f)
        self.currentTerm = persistent['currentTerm']
        self.votedFor = persistent['votedFor']
    
    ## Append Entries RPC,only use in follower state
    def appendEntries(self, request, context):
        response = raftMessage_pb2.AppendEntriesReply(term=self.currentTerm, success=True,id=self.id)
        # Append Entries Rule 1
        if request.term < self.currentTerm:
            response.success = False
            yield response
            return True
        
        if not request.entries:
            print("heartbeat")

        else:
            # Append Entries Rule 2 and 3
            if request.prevLogTerm != self.getLogTerm(request.prevLogIndex):
                print("Append Entries Rule 2 or 3: prevLogIndex not match")
                response.success = False
                print("delete log entry")
                self.deleteEntry(request.prevLogIndex)
            else:
                # Append Entries Rule 4
                self.appendEntries(request.entries)
        if request.leaderCommit > self.commitIndex:
            self.commitIndex = min(request.leaderCommit, len(self.log)-1)
        self.leaderId = request.leaderId
        return response
    
    ## Request Vote RPC,only use in follower state
    def requestVote(self, request, context):
        response = raftMessage_pb2.RequestVoteReply(term=self.currentTerm, voteGranted=True,id=self.id)
        # Request Vote Rule 1
        if request.term < self.currentTerm:
            response.voteGranted = False
            return response
        # Request Vote Rule 2
        if self.votedFor is None or self.votedFor == request.candidateId:
            if request.lastLogIndex >= len(self.log)-1 and request.lastLogTerm >= self.getLogTerm(len(self.log)-1):
                self.votedFor = request.candidateId
                return response
            else:
                self.votedFor = None
                response.voteGranted = False
                return response
        else:
            response.voteGranted = False
            print("vote for other candidate: ",self.votedFor)
            return response
    
    # ## Rules for All Servers
    # def allServers(self,message):
    #     ## All servers Rule 1
    #     if self.commitIndex > self.lastApplied:
    #         self.lastApplied += 1
    #         return self.log[self.lastApplied].command
    #     ## All servers Rule 2
    #     if message.term > self.currentTerm:
    #         self.currentTerm = message.term
    #         self.votedFor = None
    #         self.leader_selection_time = time.time() + election_timeout
    #         self.state = 'follower'
    #         self.savePersistentState()

    # ## Rules for Followers
    # def followers(self,message,messageType):

    #     reset = False
    #     ## Followers Rule 1
    #     if messageType == 'AppendEntries':
    #         reset = message.success
    #     elif messageType == 'RequestVote':
    #         reset = message.success


        
                
            

