./go-ycsb load redis -P workloads/workloada_raw -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_load.txt
wait
./go-ycsb run redis -P workloads/workloada_raw -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloada_raw.txt
wait
./go-ycsb run redis -P workloads/workloadb_raw -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloadb_raw.txt
wait
./go-ycsb run redis -P workloads/workloadc_raw -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloadc_raw.txt
wait
./go-ycsb run redis -P workloads/workloada_histogram -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloada_histogram.txt
wait
./go-ycsb run redis -P workloads/workloadb_histogram -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloadb_histogram.txt
wait
./go-ycsb run redis -P workloads/workloadc_histogram -p redis.addr=192.168.0.12:8000 -p redis.datatype=hash -p redis.mode=cluster > ./output/redis/redis_workloadc_histogram.txt
