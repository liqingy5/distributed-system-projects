# Project 1: Group Chat Command Line Application Using gRPC

## Docker setup

To make setup easier, we have provided a `Dockerfile` that can be used to set up
a Docker image with all of the necessary dependencies.

To build the image, run:

```
docker build . -t "groupchat"
```

### Basic single-container setup

To run a container using this image, you can run:

```
docker run -it --name groupchat groupchat
```

This command will give you an interactive bash shell on the container.
If you want to open additional shells on the same container (e.g. you may have
one shell for your server and one for your client), you can run (in a separate
terminal window):

```
docker exec -it groupchat bash
```

When you are done using the container, remove it with:

```
docker rm groupchat
```

## Run group chat application

To start the server, run:

```
python3 server.py
```

The server has been set to listen on port 8001

To start a client, run:

```
python3 client.py
```

After starting, to connect to the server, type

```
c localhost 8001
```

Our application support all commands showing in the project description, we also provide a demo video as reference.

[Demo](https://pitt-my.sharepoint.com/:v:/g/personal/qil77_pitt_edu/EY6yAcTqMn9BuvBo1DLV4hgBq0sNzHcwmLdZtRZpGk34yQ?e=XeTAYj)
