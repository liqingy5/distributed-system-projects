# Tikv cluster (3 nodes)

## Set up Tikv cluster

First, we need to modify the `/etc/hosts' file so we can bind the hosts name to find to pd/tikv services

```Bash
sudo vim /etc/hosts
```

Adding the folloing content into the file then save:

```Console
127.0.0.1  pd0
127.0.0.1  pd1
127.0.0.1  pd2
127.0.0.1  tikv0
127.0.0.1  tikv1
127.0.0.1  tikv2
```

And then go back to directory `./tikv`, run

```Bash
sh start_tikb.sh
```

## Test

```Bash
python test.py
```

If showing error message:

```Console
Exception: Leader of region 32 is not found
```

It means tikv's leader is not available and is normal.

Wait a period of time (Like couple of seconds), and run the `test.py` again, the exception should gone

## Clean Up

Delete containers and volumes

```Bash
sh start_tikv.sh
```
