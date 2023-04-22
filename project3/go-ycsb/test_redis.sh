./go-ycsb load redis -P workloads/workloada -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster
wait
./go-ycsb run redis -P workloads/workloada -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster
