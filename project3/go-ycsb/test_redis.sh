./go-ycsb load redis -P workloads/workloada -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_load.txt
wait
./go-ycsb run redis -P workloads/workloada -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloada.txt
wait
./go-ycsb run redis -P workloads/workloadb -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloadb.txt
wait
./go-ycsb run redis -P workloads/workloadc -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloadc.txt
