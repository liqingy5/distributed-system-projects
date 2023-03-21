#!/bin/bash
echo "Generating proto grpc files..."
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/groupChat.proto
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/raftMessage.proto
echo "DONE"
