# Instruction to run benchmark

[go-ycsb](https://github.com/pingcap/go-ycsb)

## How to run

Run the following shell scrips to run benchmark for differenent clusters:

- etcd
  ```Bash
  source test_etcd.sh
  ```
- redis
  ```Bash
  source test_redis.sh
  ```
- tikv

  ```Bash
  source test_tikv.sh
  ```

## Metrics

A successful test display the following output

```Console
Run finished, takes 107.410334ms
READ - Takes(s): 0.1, Count: 492, OPS: 6508.4, Avg(us): 652, Min(us): 144, Max(us): 31631, 50th(us): 362, 90th(us): 610, 95th(us): 734, 99th(us): 2317, 99.9th(us): 31631, 99.99th(us): 31631
TOTAL - Takes(s): 0.1, Count: 1000, OPS: 13331.7, Avg(us): 1029, Min(us): 144, Max(us): 32175, 50th(us): 659, 90th(us): 1262, 95th(us): 1553, 99th(us): 3561, 99.9th(us): 32175, 99.99th(us): 32175
UPDATE - Takes(s): 0.1, Count: 508, OPS: 6779.9, Avg(us): 1393, Min(us): 310, Max(us): 32175, 50th(us): 932, 90th(us): 1532, 95th(us): 1744, 99th(us): 31183, 99.9th(us): 32175, 99.99th(us): 32175
```

- Takes: Total time for the measurement
- Counts: Total operations
- OPS: Throughout, Operates Per Second
- Avg(us): Latency (avg) (microseconds)
- Min(us): Latency (min) (microseconds)
- Max(us): Latency (max) (microseconds)
- 50th(us): Latency (50th percentile) (microseconds)
- 90th(us): Latency (90th percentile) (microseconds)
- 95th(us): Latency (95th percentile) (microseconds)
- 99th(us): Latency (99th percentile) (microseconds)
- 99.9th(us): Latency (99.9th percentile) (microseconds)
- 99.99th(us) Latency (99.99th percentile) (microseconds)
