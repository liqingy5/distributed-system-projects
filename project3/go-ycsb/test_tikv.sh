./go-ycsb load tikv -P workloads/workloada_raw -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_load.txt
wait
./go-ycsb run tikv -P workloads/workloada_raw -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloada_raw.txt
wait
./go-ycsb run tikv -P workloads/workloadb_raw -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloadb_raw.txt
wait
./go-ycsb run tikv -P workloads/workloadc_raw -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloadc_raw.txt
wait
./go-ycsb run tikv -P workloads/workloada_histogram -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloada_histogram.txt
wait
./go-ycsb run tikv -P workloads/workloadb_histogram -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloadb_histogram.txt
wait
./go-ycsb run tikv -P workloads/workloadc_histogram -p tikv.pd=127.0.0.1:2379 > ./output/tikv/tikv_workloadc_histogramtxt
