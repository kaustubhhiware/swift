# swift
Collaborative Download: CS60002 Distributed systems project

## Running the project

We need to run a central discovery server, since KGP's internet disables ICMP messages and we cannot broadcast to computers outside our subnet.

```bash
$ python3 discovery.py
```

The IP of the discovery server must be known to every connecting node. The discovery node can also be a collaborative node.


```bash
$ python3 __main__.py
```

## Setup

```bash
$ pip3 install -r requirements.txt
```

## Collaborators

* Aditya Bhagwat [@eraseread](https://github.com/eraseread)
* Kaustubh Hiware [@kaustubhhiware](https://github.com/kaustubhhiware)
* Surya Midatala [@kofls](https://github.com/kofls)
* Pranay Pratyush [@pranaypratyush](https://github.com/pranaypratyush)

Note, run `pipreqs . --force` before pushing.