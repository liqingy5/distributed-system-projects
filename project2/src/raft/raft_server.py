import enum
import threading
import random
from cluster_config import ClusterConfig
import json
import os.path
import raft_pb2
import raft_pb2_grpc
import grpc
from concurrent import futures
import sys
import time

election_timeout_low = 1.5 #s change to 0.15 for production
election_timeout_high = 3 #s change to 0.3 for production
heartbeat_timeout = 0.5 #s change to 0.05 for production

class Role(enum.Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

def random_election_timeout():
    return random.uniform(election_timeout_low, election_timeout_high)

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


        self.log = [raft_pb2.LogEntry(term=0,command=1,value="Hello World"),raft_pb2.LogEntry(term=1,command=2,value="Hello World2")]
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

        

    #---------------------persistant state operation---------------------#
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


    #---------------------log entries operation---------------------#
    ## Save log local file
    def saveLog(self):
        filename = './logs/log_{}.json'.format(self.server_id)
        dirName = './logs'
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        entries = []
        for entry in self.log:
                entry_to_save = {'term':entry.term, 'command':entry.command, 'value':entry.value}
                entries.append(entry_to_save)
        with open(filename, 'w+') as f:
            json.dump(entries, f)
    ## Load log from local file
    def loadLog(self):
        filename = './logs/log_{}.json'.format(self.server_id)
        if not os.path.isfile(filename):
            self.saveLog()
        with open(filename, 'r') as f:
            entries = json.load(f)
        for entry in entries:
            self.log.append(raft_pb2.LogEntry(term=entry['term'],command=entry['command'],value=entry['value']))
    ## Delete log entries after index
    def deleteEntry(self, index):
        if index<0 or index>=len(self.log):
            return
        self.log = self.log[:index]
        self.saveLog()
    ## Get log entry term
    def getLogTerm(self, index):
        if(index<0 or index>=len(self.log)):
            return -1
        return self.log[index].term
    ## Append log entries
    def appendLogEntries(self, entries):
        self.log+=entries
        self.saveLog()
        return
    #---------------------on receive RPC request---------------------#
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
        # print("server {},at term {},with role {}, Receive Append Entries from leader id {}".format(self.server_id,self.current_term,self.role,request.leaderId))
        response = raft_pb2.AppendEntriesResponse(id=self.server_id,term=self.current_term, success=False)
        # if sender term is smaller than current term, reject
        if request.term < self.current_term:
            return response
        
        if not request.entries:
            print("server {},at term {},with role {}, Receive Heartbeat from leader id {}".format(self.server_id,self.current_term,self.role,request.leaderId))
        else:
            print("server {},at term {},with role {}, Receive Append Entries from leader id {}".format(self.server_id,self.current_term,self.role,request.leaderId,request.entries[0].command,request.entries[0].value))
        
        self.raft_lock.acquire()
        self.current_term = request.term
        self.voted_for = -1
        self.leader_id = request.leaderId
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
        self.raft_lock.acquire()
        self.deleteEntry(request.prevLogIndex+1)
        self.appendLogEntries(request.entries)
        response.success = True
        if request.leaderCommit > self.commitIndex:
            self.commitIndex = min(request.leaderCommit, len(self.log)-1)
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
        self.raft_lock.acquire()
        print("server {} election timeout, at term {}".format(self.server_id,self.current_term))
        self.role = Role.CANDIDATE
        self.leader_id = -1
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
        self.reset_election_timer()
            
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
                if self.votes >= (len(self.cluster_config.servers)+1)//2+1 and self.role == Role.CANDIDATE:
                    self.raft_lock.acquire()
                    self.role = Role.LEADER
                    ## reInitialize nextIndex and matchIndex after election
                    for _id in self.matchIndex.keys():
                        self.matchIndex[_id] = 0
                        self.nextIndex[_id] = len(self.log)
                    self.savePersistentState()
                    self.raft_lock.release()
                    print("server {} become leader".format(self.server_id))
                    
        except grpc.RpcError as e:
            print(f"Can not connect to server {server_id}")

    
    # once heartbeat timeout
    def start_heartbeat(self):
        if self.role == Role.LEADER:
            print("leader server {} send heartbeat".format(self.server_id))
            self.send_heartbeat()
            self.reset_election_timer()
        self.reset_heartbeat_timer()
    
    ## Leader send heartbeat to all other servers if heatbeat timeout
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
    
    ## handle client append request
    def ClientRequest(self, request, context):
        print("server {} receive client append request".format(self.server_id))
        if self.role != Role.LEADER:
            return raft_pb2.ClientAppendResponse(status=0,response="",leaderHint=self.leader_id)
        self.raft_lock.acquire()
        entry = raft_pb2.LogEntry(term=self.current_term,command=request.command,value=request.value)
        self.log.append(entry)

        ## Append entries request to all other servers
        threads = []
        for server_id, server_address in self.cluster_config.servers.items():
            if server_id == self.server_id:
                continue
            print("Server {} send append entries to server {}".format(self.server_id,server_id))
            t = threading.Thread(target=self.send_append_entries, args=(server_address,server_id,[self.log[self.nextIndex[server_id]]]))
            threads.append(t)
            t.start()
        self.raft_lock.acquire()
        self.commitIndex += 1
        self.raft_lock.release()
        return raft_pb2.ClientAppendResponse(status=1,response="success",leaderHint=self.leader_id)
    
    ## Send append entries RPC to specific server
    def send_append_entries(self,server_address,server_id,entries):
        request = raft_pb2.AppendEntriesRequest(term=self.current_term,leaderId=self.server_id,prevLogIndex=len(self.log)-1,prevLogTerm=self.getLogTerm(len(self.log)-1),entries=entries,leaderCommit=self.commitIndex)
        try:
            with grpc.insecure_channel(server_address) as channel:
                stub = raft_pb2_grpc.RaftStub(channel)
                response = stub.AppendEntries(request)
                print(f"Response from server {server_id}: {response}")

                if response.term > self.current_term:
                    self.raft_lock.acquire()
                    self.current_term = response.term
                    self.voted_for = -1
                    self.role = Role.FOLLOWER
                    self.savePersistentState()
                    self.raft_lock.release()
                if response.success:
                    self.raft_lock.acquire()
                    self.nextIndex[server_id] += 1
                    self.raft_lock.release()
                    return
        except grpc.RpcError as e:
            print(f"Can not connect to server {server_id}")

    # apply entries to state machine
    def applyCommit(self):
        while self.lastApplied <= self.commitIndex:
            self.lastApplied += 1
            entry = self.log[self.lastApplied]
            print("server {} apply log entry for term:{} ,command: {},value:{}to state machine ".format(self.server_id,entry.term,entry.command,entry.value))
def main():
    meta={1:"localhost:50051",2:"localhost:50052",3:"localhost:50053"}
    server_id = (int)(sys.argv[1])
    server_address = meta[server_id]
    server = RaftServer(server_id,meta)
    server.matchIndex = {_id:0 for _id in meta.keys() if _id != server_id}
    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServicer_to_server(server, grpc_server)

    host, port = server_address.split(":")
    grpc_server.add_insecure_port(f"{host}:{port}")
    grpc_server.start()
    print(f"Server {server_id} started at {server_address}")


    try:
        while True:
            time.sleep(60 * 60 * 24)  # Run servers indefinitely
    except KeyboardInterrupt:
        server.stop()
if __name__ == "__main__":
    main()

