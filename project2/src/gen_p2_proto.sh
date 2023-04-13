#!/bin/bash
echo "Generating project 2 grpc files..."
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/group_chat.proto
echo "DONE"