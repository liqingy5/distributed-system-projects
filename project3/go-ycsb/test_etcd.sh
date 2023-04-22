./go-ycsb load etcd -P workloads/workloada -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s
wait
./go-ycsb run etcd -P workloads/workloada -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s
