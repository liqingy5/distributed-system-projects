#!/bin/bash
echo "Generating raft grpc files..."
python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. ./raft.proto
echo "DONE"