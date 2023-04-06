import grpc
import raft_pb2
import raft_pb2_grpc

class RaftClient:
    def __init__(self, id,cluster_config):
        self.cluster_config = cluster_config
        self.id = id
    
    def request_vote(self, term, candidateId,lastLogIndex,lastLogTerm):
        while True:
            for server_id, server_address in self.cluster_config.servers.items():
                if server_id == self.id:
                    continue
                print("send request vote to server",server_id)
                try:
                    with grpc.insecure_channel(server_address) as channel:
                        stub = raft_pb2_grpc.RaftStub(channel)
                        response = stub.RequestVote(raft_pb2.VoteRequest(term=term,candidateId=candidateId,lastLogIndex=lastLogIndex,lastLogTerm=lastLogTerm))
                        print(f"Response from server {server_id}: {response}")

                except grpc.RpcError as e:
                    print(f"Error connecting to server {server_id}: {e}")

    def append_entries(self, server_id, term, leaderId,prevLogIndex,prevLogTerm,entries,leaderCommit):
        while True:
            for server_id, server_address in self.cluster_config.servers.items():
                if server_id == self.id:
                    continue
                print("send append entries to server",server_id)
                try:
                    with grpc.insecure_channel(server_address) as channel:
                        stub = raft_pb2_grpc.RaftStub(channel)
                        response = stub.AppendEntries(raft_pb2.AppendEntriesRequest(term=term,leaderId=leaderId,prevLogIndex=prevLogIndex,prevLogTerm=prevLogTerm,entries=entries,leaderCommit=leaderCommit))
                        print(f"Response from server {server_id}: {response}")

                except grpc.RpcError as e:
                    print(f"Error connecting to server {server_id}: {e}")

        
