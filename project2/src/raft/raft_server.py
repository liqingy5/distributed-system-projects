import enum
import threading
import random
from cluster_config import ClusterConfig
import json
import os.path
import raft_pb2
import raft_pb2_grpc
import grpc
import concurrent

election_timeout_low = 5 #s change to 0.15 for production
election_timeout_high = 8 #s change to 0.3 for production
heartbeat_timeout = 3 #s change to 0.05 for production

class Role(enum.Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

def random_election_timeout():
    return random.randint(election_timeout_low, election_timeout_high)

class Entry:
    def __init__(self,term,command):
        self.term = term
        self.command = command

class RaftServer(raft_pb2_grpc.RaftServicer):
    def __init__(self, server_id,meta):
        self.server_id = server_id
        self.role = Role.CANDIDATE
        
        self.leader_id = -1

        self.cluster_config = ClusterConfig(meta)         
         # Persistent state on all servers:
        self.current_term = 0
        self.voted_for = -1
        self.loadPersistentState() ## load persistent state from file if exist


        self.log = []
        self.loadLog() ## load log from file if exist

        # Volatile state on all servers:
        
        self.commitIndex = 0 ## index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.lastApplied = 0 ## index of highest log entry applied to state machine (initialized to 0, increases monotonically)
        
        # Volatile state on leaders:
        
        self.nextIndex = {_id:0 for _id in meta.keys() if _id!=server_id} ## for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.matchIndex = {_id:0 for _id in meta.keys() if _id != server_id} ## for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)

        self.election_timer = None
        self.heartbeat_timer = None
        self.reset_election_timer()
        self.reset_heartbeat_timer()

        self.votes = 0
        self.vote_lock = threading.Lock()
        self.raft_lock = threading.Lock()

        

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
        self.raft_lock.acquire()
        if index<0 or index>=len(self.log):
            return
        self.log = self.log[:index]
        self.saveLog()
        self.raft_lock.release()
    def getLogTerm(self, index):
        if(index<0 or index>=len(self.log)):
            return -1
        return self.log[index].term
    def appendLogEntries(self, entries):
        self.raft_lock.acquire()
        self.log+=entries
        self.saveLog()
        self.raft_lock.release()
        return
    # On receive request vote RPC
    def RequestVote(self, request, context):
        print("Server {} current term is {} ,receive Vote request from Server {}, at term {} ".format(self.server_id, self.current_term,request.candidateId,request.term))
        response = raft_pb2.VoteResponse(id=self.server_id,term=self.current_term, voteGranted=False)
        # RequestVote Rule 1
        ## Reply false if term < currentTerm
        if (request.term < self.current_term) or (request.term == self.current_term and self.voted_for != -1 and self.voted_for != request.candidateId):
            return response
        
        ## Other server has higher term
        if request.term > self.current_term:
            self.raft_lock.acquire()
            self.current_term = request.term
            self.voted_for = -1
            self.role = Role.FOLLOWER
            self.savePersistentState()
            self.raft_lock.release()
        # RequestVote Rule 2
        if self.voted_for == -1 or self.voted_for == request.candidateId:
            if (request.lastLogTerm >= self.getLogTerm(len(self.log)-1)) and (request.lastLogIndex >= len(self.log)-1):
                self.raft_lock.acquire()
                self.voted_for = request.candidateId
                self.savePersistentState()
                response.voteGranted = True
                ## Reset election timer if vote granted
                self.reset_election_timer()
                self.raft_lock.release()
        
        return response
    # On receive append entries RPC
    def AppendEntries(self, request, context):
        print("server {},at term {},with role {}, Receive Append Entries from leader id {}".format(self.server_id,self.current_term,self.role,request.leaderId))
        response = raft_pb2.AppendEntriesResponse(id=self.server_id,term=self.current_term, success=False)
        # if sender term is smaller than current term, reject
        if request.term < self.current_term:
            return response
        
        if request.term > self.current_term:
            self.raft_lock.acquire()
            self.current_term = request.term
            self.voted_for = -1
            self.role = Role.FOLLOWER
            self.savePersistentState()
            self.raft_lock.release()
        response.term = self.current_term
        self.reset_election_timer()
        # if not request.entries:
        #     self.reset_heartbeat_timer()
        
        # Reply false if log doesn’t contain an entry at prevLogIndex whose term matches prevLogTerm
        if request.prevLogIndex >= len(self.log) or self.getLogTerm(request.prevLogIndex) != request.prevLogTerm:
            return response
        self.deleteEntry(request.prevLogIndex+1)
        self.appendLogEntries(request.entries)
        response.success = True
        if request.leaderCommit > self.commitIndex:
            self.raft_lock.acquire()
            oldCommit = self.commitIndex
            self.commitIndex = min(request.leaderCommit, len(self.log)-1)
            if self.commitIndex > oldCommit:
                self.applyCommit()
            self.raft_lock.release()
        return response

    ## Election timer
    def reset_election_timer(self):
        if self.election_timer is not None:
            self.election_timer.cancel()
        self.election_timer = threading.Timer(random_election_timeout(), self.start_election)
        self.election_timer.start()
    
    ## Heartbeat timer
    def reset_heartbeat_timer(self):
        if self.heartbeat_timer is not None:
            self.heartbeat_timer.cancel()
        self.heartbeat_timer = threading.Timer(heartbeat_timeout, self.start_heartbeat)
        self.heartbeat_timer.start()

    # once election timeout
    def start_election(self):
        print(self.raft_lock)
        self.raft_lock.acquire()
        self.role = Role.CANDIDATE
        self.current_term += 1
        self.voted_for = self.server_id
        request = raft_pb2.VoteRequest(term=self.current_term,candidateId=self.server_id,lastLogIndex=len(self.log)-1,lastLogTerm=self.getLogTerm(len(self.log)-1))
        self.savePersistentState()
        self.raft_lock.release()
        print("server {} start election, at term {}".format(self.server_id,self.current_term))
        threads = []
        self.votes = 1
        ## Send election request to all other servers at the same time using threads
        for server_id, server_address in self.cluster_config.servers.items():
            ## If candidate Id is same as server id, skip
            if server_id == self.server_id:
                continue
            print("server {} send request vote to server {}".format(self.server_id,server_id))
            t = threading.Thread(target=self.send_request_vote, args=(request,server_address,server_id))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
            
    # send request vote RPC to specific server
    def send_request_vote(self, request,server_address,server_id):
        try:
            with grpc.insecure_channel(server_address) as channel:
                stub = raft_pb2_grpc.RaftStub(channel)
                response = stub.RequestVote(request)
                print(f"Response from server {server_id},at term:{response.term}, granted: {response.voteGranted}")
                if response.voteGranted is False:
                    return
                # other server has higher term,we should become follower
                if response.term > self.current_term:
                    self.raft_lock.acquire()
                    self.current_term = response.term
                    self.voted_for = -1
                    self.role = Role.FOLLOWER
                    self.savePersistentState()
                    self.raft_lock.release()
                self.vote_lock.acquire()
                self.votes += 1
                self.vote_lock.release()
                ## Have majority votes
                if self.votes > len(self.cluster_config.servers)/2 and self.role == Role.CANDIDATE:
                    self.raft_lock.acquire()
                    self.role = Role.LEADER
                    ## reInitialize nextIndex and matchIndex after election
                    for _id in self.matchIndex.keys():
                        self.matchIndex[_id] = 0
                        self.nextIndex[_id] = len(self.log)
                    self.reset_election_timer() ## reset election timer
                    self.savePersistentState()
                    self.raft_lock.release()
                    # self.reset_heartbeat_timer() ## start heartbeat timer
                    print("server {} become leader".format(self.server_id))
        except grpc.RpcError as e:
            print(f"Error connecting to server {server_id}: {e}")
    
    # once heartbeat timeout
    def start_heartbeat(self):
        print("server {} start heartbeat".format(self.server_id))
        if self.role == Role.LEADER:
            self.send_heartbeat()
            self.reset_heartbeat_timer()
     
    def send_heartbeat(self):
        threads = []
        for server_id, server_address in self.cluster_config.servers.items():
            if server_id == self.server_id:
                continue
            print("Server {} send heartbeat to server {}".format(self.server_id,server_id))
            t = threading.Thread(target=self.send_append_entries, args=(server_address,server_id,[]))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
    
    def send_append_entries(self,server_address,server_id,entries):
        request = raft_pb2.AppendEntriesRequest(term=self.current_term,leaderId=self.server_id,prevLogIndex=len(self.log)-1,prevLogTerm=self.getLogTerm(len(self.log)-1),entries=entries,leaderCommit=self.commitIndex)
        try:
            with grpc.insecure_channel(server_address) as channel:
                stub = raft_pb2_grpc.RaftStub(channel)
                request = raft_pb2.AppendEntriesRequest(term=self.current_term,leaderId=self.server_id,prevLogIndex=len(self.log)-1,prevLogTerm=self.getLogTerm(len(self.log)-1),entries=entries,leaderCommit=self.commitIndex)
                response = stub.AppendEntries(request)
                print(f"Response from server {server_id}: {response}")

                if response.term > self.current_term:
                    self.raft_lock.acquire()
                    self.current_term = response.term
                    self.voted_for = -1
                    self.role = Role.FOLLOWER
                    self.savePersistentState()
                    self.raft_lock.release()
        except grpc.RpcError as e:
            print(f"Error connecting to server {server_id}: {e}")

    # apply entries to state machine
    def applyCommit(self):
        pass


