# Group chat system with server replication

The replica version of group chat system, client can connect to mutiple servers to use the service. Our system can provide availability, partition tolerance and eventual consistency as much as possible.

## Prerequisites

- Python 3.11.1
- pip 22.3.1

### Set up virtual environment

```Bash
python -m venv env
```

```Bash
source env/bin/activate
```

### Install dependencies

```Bash
pip install -r requirements.txt.
```

## Generate gRPC code

```Bash
source generate_proto.sh
```

### Run Server

To run the server with id 1

```Bash
python server.py -id 1
```

We have configure the server ip address in config.json and config_test.json file, while the ip addresses in config_test.json are used for the bridge network tests in docker containers. To start the server on local machine, run:

```Bash
python server.py -id 1 -D
```

With `-D` flag, the server read the ip address in config.json, and start locally.

### Run client

To run the client application

```Bash
python client.py
```

When starting, to connect to the server with id 1, if you are running the system locally, run:

```Bash
c localhost 50051
```

Otherwise

```Bash
c cs2510_server1 8081
```

or

```Bash
c 172.30.100.101 8081
```
