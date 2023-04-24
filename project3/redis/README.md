# Redis cluster set up (3 masters - 3 slaves)

## Set up redis cluster

To create a redis cluster and can be accessed from the outside of the docker container. First open docker-compose.yaml, and in the environment tag for each node, change `REDIS_CLUSTER_ANNOUNCE_IP` to the ip address of your local machine.

Then, run:

```Bash
sh start_redis.sh
```

## Test

Change the ip address to yours

```Bash
python test.py
```

## Clean Up

Delete containers and volumes

```Bash
sh reset_redis.sh
```
