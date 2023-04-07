import enum
import random
import threading
from cluster_config import ClusterConfig
import json
import os.path
import raft_pb2
import raft_pb2_grpc
from raft_client import RaftClient

election_timeout = 20 #s change to 0.15 for production
heartbeat_timeout = 15 #s change to 0.1 for production

class Role(enum.Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftServer(raft_pb2_grpc.RaftServicer):
    def __init__(self, server_id,meta):
        self.server_id = server_id
        self.role = Role.CANDIDATE
        
        self.leader_id = -1

        self.cluster_config = ClusterConfig(meta)
        self.client = RaftClient(self.server_id,self.cluster_config) ## Used to send RPCs to other servers for Leader
         
         # Persistent state on all servers:
        self.current_term = 0
        self.voted_for = None
        self.loadPersistentState() ## load persistent state from file if exist


        self.log = []
        self.loadLog() ## load log from file if exist

        # Volatile state on all servers:
        
        self.commitIndex = 0 ## index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.lastApplied = 0 ## index of highest log entry applied to state machine (initialized to 0, increases monotonically)
        
        # Volatile state on leaders:
        
        self.nextIndex = {} ## for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.matchIndex = {_id:0 for _id in meta.keys() if _id != server_id} ## for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)

        self.election_timer = None
        self.heartbeat_timer = None
        self.reset_election_timer()
        self.reset_heartbeat_timer()
        

    # Persistent state operations
    def savePersistentState(self):
        persistent = {'current_term':self.current_term, 'voted_for':self.voted_for}
        dirName = './states'
        filename = './states/persistent_state_{}.json'.format(self.server_id)
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        with open(filename, 'w+') as f:
            json.dump(persistent, f)
    def loadPersistentState(self):
        filename = './states/persistent_state_{}.json'.format(self.server_id)
        if not os.path.isfile(filename):
            self.savePersistentState()
        with open(filename, 'r') as f:
            persistent = json.load(f)
        self.current_term = persistent['current_term']
        self.voted_for = persistent['voted_for']


    ## Log entries operations
    def saveLog(self):
        filename = './logs/log_{}.json'.format(self.server_id)
        dirName = './logs'
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        with open(filename, 'w+') as f:
            json.dump(self.log, f)
    def loadLog(self):
        filename = './logs/log_{}.json'.format(self.server_id)
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

    def RequestVote(self, request, context):
        self.reset_election_timer()
        print("Request Vote from: ",request.candidateId)
        
        response = raft_pb2.VoteResponse(id=self.server_id,term=self.current_term, voteGranted=False)
        if request.term < self.current_term:
            return response
        # Request Vote Rule 2
        if self.voted_for is None or self.voted_for == request.candidateId:
            if request.lastLogIndex >= len(self.log)-1 and request.lastLogTerm >= self.getLogTerm(len(self.log)-1):
                self.voted_for = request.candidateId
                response.voteGranted = True
                return response
            else:
                self.voted_for = None
                return response
        else:
            print("Already voted for other candidate: ",self.voted_for)
            return response

    def AppendEntries(self, request, context):
        self.reset_election_timer()
        self.reset_heartbeat_timer()

        response = raft_pb2.AppendEntriesResponse(id=self.server_id,term=self.current_term, success=False)
        # Append Entries Rule 1
        if request.term < self.current_term:
            return response
        
        if not request.entries:
            print("heartbeat")

        else:
            # Append Entries Rule 2 and 3
            if request.prevLogTerm != self.getLogTerm(request.prevLogIndex):
                print("Append Entries Rule 2 or 3: prevLogIndex not match")
                print("delete log entry")
                self.deleteEntry(request.prevLogIndex)
            else:
                # Append Entries Rule 4
                self.appendEntries(request.entries)
        if request.leaderCommit > self.commitIndex:
            self.commitIndex = min(request.leaderCommit, len(self.log)-1)
        self.leader_id = request.leaderId
        response.success = True
        return response


    def reset_election_timer(self):
        if self.election_timer is not None:
            self.election_timer.cancel()

        print("election timer reset")
        self.election_timer = threading.Timer(election_timeout, self.start_election)
        self.election_timer.start()
    
    def reset_heartbeat_timer(self):
        if self.heartbeat_timer is not None:
            self.heartbeat_timer.cancel()

        print("heartbeat timer reset")
        self.heartbeat_timer = threading.Timer(heartbeat_timeout, self.start_heartbeat)
        self.heartbeat_timer.start()

    def start_election(self):
        self.client.request_vote(self.server_id, self.current_term, len(self.log)-1, self.getLogTerm(len(self.log)-1))
    
    def start_heartbeat(self):
        self.client.append_entries(self.server_id, self.current_term,self.leader_id, len(self.log)-1, self.getLogTerm(len(self.log)-1), [], self.commitIndex)

    # ## Rules for All Servers
    # def all_servers(self,message):
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
