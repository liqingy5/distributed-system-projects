# Etcd cluster set up (3 nodes)

Etcd setting is referenced from [garutilorenzo](https://github.com/garutilorenzo/docker-etcd-cluster)

## Set up etcd cluster

```Bash
sh start_redis.sh
```

## Test

```Bash
python main.py
```

## Clean Up

Delete containers and volumes

```Bash
sh reset_redis.sh
```
