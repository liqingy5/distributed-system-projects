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

To start a client,run:

```
python3 client.py
```

<!-- ### Multiple container setup

To run applications over multiple machines.

To create a bridge network named `cs2510`, you can run (on your host, not inside a
container):

```
docker network create --driver bridge cs2510
```

Then, to create two containers `server` and `client` that both connect to the
bridge, you can run (in two separate terminal windows):

```
docker run -it --name server --network cs2510 GroupChat
docker run -it --name client --network cs2510 GroupChat
```

With this setup, you can use the names of the containers (i.e. `server` and
`client`) as the hostnames for communication. Alternatively, you can find the
IP address for each container by running `ip addr` in the container and then
use the IP addresses.

When you are done, remove both containers:

```
docker rm server
docker rm client
``` -->
