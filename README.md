# swift
```
   _____         _ ______ 
  / ___/      __(_) __/ /_
  \__ \ | /| / / / /_/ __/
 ___/ / |/ |/ / / __/ /_  
/____/|__/|__/_/_/  \__/ 
```

Collaborative Download: CS60002 Distributed systems project

Swift is designed to use to solve the problem of huge file downloads by leveraging a distributed approach. It divided a file into chunks, which are assigned to be downloaded by its peers/ collaborators. Once every peer completes its download, the chunk is sent back to the requester and local cache is deleted. The requester finally reassembles the requested file by merging the chunks it receives from its peers.

Swift is designed to work on a lcoal network of systems (strongly connected), which are also connected to internet. A special node keeps track of nodes in this collaborative network, updating and sending peers list to any new / downloading node. This special node is called the discovery, and it does not itself participate in the download process. All other nodes execute a server and a client, the server for handling downloads and the client for handling user requests.

## Features

* Crash resistant - If a node crashes during download, its job is automatically reassinged to all other nodes.
* Simultaneous downloads - Since every download is executed on a thread, multiple nodes can request for multiple files.
* Speedup -TBD

## Setup

```bash
$ pip3 install -r requirements.txt
```

```bash
sudo ufw allow from any to any port 8000 proto tcp
sudo ufw allow from any to any port 5000 proto tcp
sudo ufw allow from any to any port 6000 proto tcp
```

## Running the project

We need to run a central discovery server, since KGP's internet disables ICMP messages and we cannot broadcast to computers outside our subnet.

```bash
$ python3 discovery.py
```

The IP of the discovery server must be known to every connecting node. The discovery node can also be a collaborative node.

```bash
$ python3 node.py
```

## Collaborators

* Kaustubh Hiware [@kaustubhhiware](https://github.com/kaustubhhiware)
* Surya Midatala [@kofls](https://github.com/kofls)
* Aditya Bhagwat [@eraseread](https://github.com/eraseread)
* Pranay Pratyush [@pranaypratyush](https://github.com/pranaypratyush)

Note, run `pipreqs . --force` before pushing.