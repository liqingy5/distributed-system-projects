./go-ycsb load tikv -P workloads/workloada -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_load.txt
wait
./go-ycsb run tikv -P workloads/workloada -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloada.txt
wait
./go-ycsb run tikv -P workloads/workloadb -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloadb.txt
wait
./go-ycsb run tikv -P workloads/workloadc -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloadc.txt