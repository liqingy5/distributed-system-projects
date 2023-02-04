# Group chat Server/Client

A simple group chat server/client implemented with [gRPC](https://grpc.io) in Python.

## Prerequisites

- Python 3.7 or higher
- pip version 9.0.1 or higher

### gRPC

```Bash
python -m pip install grpcio
```

### gRPC tools

```Bash
python -m pip install grpcio-tools
```

## Generate gRPC code

```Bash
python -m grpc_tools.protoc -I./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/groupChat.proto
```
