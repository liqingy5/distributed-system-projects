import grpc
import raft_pb2
import raft_pb2_grpc
import time

class RaftClient:
    def __init__(self,cluster_config):
        self.cluster_config = cluster_config
    
    def request_vote(self, request):
        votes = 1
        for server_id, server_address in self.cluster_config.servers.items():
            ## If candidate Id is same as server id, skip
            if server_id == request.candidateId:
                continue
            print("send request vote to server",server_id)
            try:
                with grpc.insecure_channel(server_address) as channel:
                    stub = raft_pb2_grpc.RaftStub(channel)
                    response = stub.RequestVote(request)
                    print(f"Response from server {server_id}: {response}")
                    if(response.voteGranted):
                        votes+=1

            except grpc.RpcError as e:
                print(f"Error connecting to server {server_id}: {e}")
        return votes

    def append_entries(self, server_id, term, leaderId,prevLogIndex,prevLogTerm,entries,leaderCommit):
        while True:
            for server_id, server_address in self.cluster_config.servers.items():
                if server_id == self.id:
                    continue
                time.sleep(3) ## debug purpose, delete when productino
                print("send append entries to server",server_id)
                try:
                    with grpc.insecure_channel(server_address) as channel:
                        stub = raft_pb2_grpc.RaftStub(channel)
                        response = stub.AppendEntries(raft_pb2.AppendEntriesRequest(term=term,leaderId=leaderId,prevLogIndex=prevLogIndex,prevLogTerm=prevLogTerm,entries=entries,leaderCommit=leaderCommit))
                        print(f"Response from server {server_id}: {response}")

                except grpc.RpcError as e:
                    print(f"Error connecting to server {server_id}: {e}")

        
