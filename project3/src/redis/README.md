# Redis cluster set up (3 masters - 3 slaves)

## Set up redis cluster

To create a redis cluster and can be accessed from the outside of the docker container. First open docker-compose.yaml, and in the environment tag for each node, change `REDIS_CLUSTER_ANNOUNCE_IP` to the ip address of your local machine.

Then, run:

```Bash
docker compoese up -d
```

## Clean Up

Delete containers and volumes

```Bash
docker compose down && docker volume prune -f
```
