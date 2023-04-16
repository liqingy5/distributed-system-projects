# Project 2: Replicated version of the group chat system

## Docker setup

To make setup easier, we have provided a `Dockerfile` that can be used to set up
a Docker image with all of the necessary dependencies.

To build the image, run:

```Bash
docker build . -t "cs2510_p2"
```

## Test instruction

### Environment set up

In src directory, run the test script to set up docker containers with bridge network. (To instructor: we have configure the test script to match our application, please use our test_p2.py in src directory for testing)

```Bash
python test_p2.py init
```

Wait the script to complete, then you should be able to see 5 containers running on docker dashboard, or you can confirm by running

```Bash
docker ps
```

if you want to see the output from the chat_server process on server 1, you can check the logs on docker dashboard or run with the command

```Bash
docker logs cs2510_server1
```

### Running Client Programs

To run one client that connects to the bridge network

```Bash
docker run -it --cap-add=NET_ADMIN --network cs2510 --rm --name cs2510_client1 cs2510_p2 /bin/bash
```

To run multiple clients, you just need to give each one a different name using the --name parameter.

To start the client.py, run

```Bash
python3 client.py
```

To connect to the server to with server id 1 in the docker container, you can either type

```
c cs2510_server1 8081
```

or

```
c 172.30.100.101 8081
```

There are total 5 servers and id from 1 to 5, by replace the id parameter in cs2510_server[id] or 172.30.100.10[id] can connect to different servers

### Setting loss rates:

```Bash
python test_p2.py loss container1 container2 loss-rate
```

This will add loss-rate percent loss between servers with IDs container1 and container2. For example:

```Bash
python test_p2.py loss 1 2 20
```

adds 20% loss between servers 1 and 2.

### Creating partitions:

```Bash
python test_p2.py partition 1,2 3,4,5
```

Creates 2 partitions, one containing servers 1 and 2, and another containing servers 3, 4, and 5. NOTE: Creating/modifying partitions removes any loss that was previously added between containers.

### Crashing and restarting servers:

```Bash
python test_p2.py kill 1
python test_p2.py relaunch 1
```

The first command will crash server 1, and the second will restart it.

### Cleaning up:

To remove all server container

```Bash
python test_p2.py rm
```
