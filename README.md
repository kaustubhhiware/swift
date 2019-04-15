# swift
Collaborative Download: CS60002 Distributed systems project

## Running the project

We need to run a central discovery server, since KGP's internet disables ICMP messages and we cannot broadcast to computers outside our subnet.

```bash
$ python3 discovery_server.py
```

The IP of the discovery server must be known to every connecting node. The discovery node can also be a collaborative node.


```bash
$ python3 client.py -d <DISCOVERY_SERVER_IP>
```

## Setup

```bash
$ pip3 install -r requirements.txt
```

## Notes

When changing the grpc protocol, the python stubs will have to be created by running the following from the root project directory:

```bash
$ python -m grpc_tools.protoc -I./protos  --python_out=. --grpc_python_out=. ./protos/discover.proto
```

```bash
iptables -A INPUT -i wlp3s0 -p tcp --dport 4444 -j ACCEPT
iptables -A INPUT -i wlp3s0 -p tcp --dport 8192 -j ACCEPT
```
## Collaborators

* Aditya Bhagwat [@eraseread](https://github.com/eraseread)
* Kaustubh Hiware [@kaustubhhiware](https://github.com/kaustubhhiware)
* Surya Midatala [@kofls](https://github.com/kofls)
* Pranay Pratyush [@pranaypratyush](https://github.com/pranaypratyush)

Note, run `pipreqs . --force` before pushing.