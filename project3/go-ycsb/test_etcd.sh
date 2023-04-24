./go-ycsb load etcd -P workloads/workloada -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_load.txt
wait
./go-ycsb run etcd -P workloads/workloada -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloada.txt
wait
./go-ycsb run etcd -P workloads/workloadb -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloadb.txt
wait
./go-ycsb run etcd -P workloads/workloadc -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloadc.txt
