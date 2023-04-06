import time
import grpc
from concurrent import futures
from raft_server import RaftServer
from cluster_config import ClusterConfig
from raft_client import RaftClient
import raft_pb2_grpc

def main():
    meta={1:"localhost:50051",2:"localhost:50052",3:"localhost:50053"}

    servers = []
    for server_id, server_address in meta.items():
        server = RaftServer(server_id,meta)
        server.matchIndex = {_id:0 for _id in meta.keys() if _id != server_id}
        grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        raft_pb2_grpc.add_RaftServicer_to_server(server, grpc_server)

        host, port = server_address.split(":")
        grpc_server.add_insecure_port(f"{host}:{port}")
        grpc_server.start()
        servers.append(grpc_server)

    print("Raft servers started")


    try:
        while True:
            time.sleep(60 * 60 * 24)  # Run servers indefinitely
    except KeyboardInterrupt:
        for server in servers:
            server.stop(0)

if __name__ == "__main__":
    main()
