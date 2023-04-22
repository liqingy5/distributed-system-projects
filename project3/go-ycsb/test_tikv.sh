./go-ycsb load tikv -P workloads/workloada -p tikv.pd=127.0.0.1:2379
wait
./go-ycsb run tikv -P workloads/workloada -p tikv.pd=127.0.0.1:2379
