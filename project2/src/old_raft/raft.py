## Just pseudocode for now, can change later
import asyncio
import grpc
import time
import sys
import json
import threading
import os.path
import raftMessage_pb2
import raftMessage_pb2_grpc
from concurrent import futures

election_timeout = 150 #ms
heartbeat_timeout = 100 #ms

class RaftClient:
    def __init__(self, ip, addr):
        self.channel = grpc.insecure_channel('{}:{}'.format(ip, addr),options=(('grpc.enable_http_proxy', 0),))
        self.stub = raftMessage_pb2_grpc.raftMessageStub(self.channel)

    def sendRequestVoteRPC(self):
        request = raftMessage_pb2.RequestVoteArgs(
                term=0,
                candidateId=0,
                lastLogIndex=0,
                lastLogTerm=0
            )
        while True:
            time.sleep(5)
            try:
                response = self.stub.requestVote(request, timeout=election_timeout)
                print("requestVoteRPC")
                print(response)
            except Exception as e:
                print(e)

    def sendAppendEntriesRPC(self):
        request = raftMessage_pb2.AppendEntriesArgs(
                term=0,
                leaderId=0,
                prevLogIndex=0,
                prevLogTerm=0,
                entries=[],
                leaderCommit=0
            )
        while True:
            time.sleep(5)
            try:
                response = self.stub.appendEntries(request, timeout=election_timeout)
                print("AppendEntriesRPC")
                print(response)
            except Exception as e:
                print(e)

    def request(self):
        appendEntries_thread = threading.Thread(target=self.sendAppendEntriesRPC,args=())
        appendEntries_thread.start()

        requestVote_thread = threading.Thread(target=self.sendRequestVoteRPC,args=())
        requestVote_thread.start()
            
        requestVote_thread.join()
        appendEntries_thread.join()

class RaftNode(raftMessage_pb2_grpc.raftMessageServicer):
    def __init__(self, _id, meta):
        self.id = _id
        self.addr = meta[id]["ip"] ## address of this server (e.g., 'localhost')
        self.port = meta[id]["port"] ## port of this server (e.g., 50051)
        self.state = 'candidate'
        self.peers = {_id:meta[_id] for _id in meta.keys() if _id!=self.id}
        

        # Persistent state on all servers:
        
        self.currentTerm = 0 ## latest term server has seen (initialized to 0 on first boot, increases monotonically)
        self.votedFor = None ## candidateId that received vote in current term (or null if none)
        self.loadPersistentState() ## load persistent state from file if exist
        
        self.log = [] ## log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)
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
        self.voteIds={_id:0 for _id in meta.keys() if _id!=self.id}

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
        dirName = './logs'
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        with open(filename, 'w+') as f:
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
        dirName = './states'
        filename = './states/persistent_state_{}.json'.format(self.id)
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        with open(filename, 'w+') as f:
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
            return response
        
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

    def run(self):
        pool = futures.ThreadPoolExecutor(max_workers=5)
        for id in self.peers.keys():
            peer = RaftClient(self.peers[id]['ip'],self.peers[id]['port'])
            pool.submit(peer.request)



        

    
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
def start_server(id,port,meta):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=100))
    node = RaftNode(id,meta)
    raftMessage_pb2_grpc.add_raftMessageServicer_to_server(node, server)
    server.add_insecure_port('[::]:{}'.format(port))
    server.start()
    print("server {} start, listening on port {}".format(id,port))
    node.run()
    server.wait_for_termination()



if __name__ == '__main__':
    meta = {1:{"ip":"localhost","port":50051},2:{"ip":"localhost","port":50052}}
    id =  int(sys.argv[1])
    
    server_thread = threading.Thread(target=start_server, args=(id,meta[id]["port"],meta,))
    server_thread.start()

    # Start the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

        
                
            

