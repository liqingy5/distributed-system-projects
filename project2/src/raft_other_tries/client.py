import grpc
import sys
import raft_pb2
import raft_pb2_grpc

class raft_client():
 def __init__(self):    
  print("opening channel")
  self.peers = {}
  self.stubs = {}
  with open("./config.txt", "r") as f:
     line = f.readline()
     while (line):
        id,addr = line.split()
        self.peers[int(id)] = addr
        channel = grpc.insecure_channel(addr)
        stub = raft_pb2_grpc.RaftServerStub(channel)
        self.stubs[int(id)] = stub
        line = f.readline()

 def client_append_request(self,string):
  k = string
  for id in self.stubs.keys():
    stub = self.stubs[id]
    print("Contacting", self.peers[id])
    try:
      self.req = stub.ClientAppend(raft_pb2.ClientAppendRequest(decree=k))
      print("got client append response: {}".format(self.req))
    except:
      print("cannot connect to " + str(self.peers[id]))
 def client_req_index(self, index_num):
  k = index_num
  for id in self.stubs.keys():
    stub = self.stubs[id]
    try:
      self.req = stub.ClientRequestIndex(raft_pb2.ClientRequestIndexRequest(index=int(k)))
      print("got client request index response: {}".format(self.req))
    except:
      print("cannot connect to " + str(self.peers[id]))

if __name__ == '__main__':
  client = raft_client()
  while(True):
    d = input("Enter 1. Client Append request ; 2. Client request Index\n")
    if (int(d) == 1):
        f = input("Enter decree:\n")
        client.client_append_request(f)
    else:
        f = input("Enter Index value to be requested:\n")
        client.client_req_index(f)