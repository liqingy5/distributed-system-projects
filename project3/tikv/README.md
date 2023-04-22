# Tikv cluster

## Set up Tikv cluster use TiUP

Install TiUP by executing the following command:

```Bash
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
```

Set the TiUP environment variables:

- Redeclare the global environment variables:

  ```Bash
  source ~/.bash_profile
  ```

- Confirm whether TiUP is installed:

  ```Bash
  tiup
  ```

Update the TiUP Playground component to the latest version

```Bash
tiup update --self && tiup update playground
```

Execute the following command to start a local TiKV cluster:

```Bash
tiup playground --mode tikv-slim
```

## Write data to and read data from the TiKV cluster

### Use Java

- Download the JAR files using the following commands: (Already include)
  ```Bash
  curl -o tikv-client-java.jar https://github.com/tikv/client-java/releases/download/v3.2.0-rc/tikv-client-java-3.2.0-SNAPSHOT.jar -L && \
  curl -o slf4j-api.jar https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.16/slf4j-api-1.7.16.jar
  ```
- Install jshell. The JDK version should be 9.0 or later.

- Try the RAW KV API.

  ```Bash
  jshell --class-path tikv-client-java.jar:slf4j-api.jar --startup test_raw.java

  ```

### Use Python

- Install the tikv-client python package. (Already include in requirements.txt)

  ```Bash
  pip install tikv-client

  ```

- run tikv client driver

  ```Bash
  python test_raw.py
  ```

- If showing error, try switch to rosetta terminal on MacOS or use python3-intel64 instead

## Stop and Delete Tikv cluster

- To stop the TiKV cluster, get back to the terminal session in which you have started the TiKV cluster. Press Ctrl + C and wait for the cluster to stop.

- After the cluster is stopped, to delete the cluster, execute the following command:

  ```Bash
  tiup clean --all

  ```
