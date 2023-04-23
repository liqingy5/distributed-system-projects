./go-ycsb load etcd -P workloads/workloada_raw -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_load.txt
wait
./go-ycsb run etcd -P workloads/workloada_raw -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloada_raw.txt
wait
./go-ycsb run etcd -P workloads/workloadb_raw -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloadb_raw.txt
wait
./go-ycsb run etcd -P workloads/workloadc_raw -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloadc_raw.txt
wait
./go-ycsb run etcd -P workloads/workloada_histogram -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloada_histogram.txt
wait
./go-ycsb run etcd -P workloads/workloadb_histogram -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloadb_histogram.txt
wait
./go-ycsb run etcd -P workloads/workloadc_histogram -p etcd.endpoints=127.0.0.1:50051 -p etcd.dial_timeout=2s > ./output/etcd/etcd_workloadc_histogram.txt
