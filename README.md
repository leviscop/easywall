# Guide

## Dockerfile

This container is based on the official [python's docker image](https://hub.docker.com/_/python) `python:3.9-buster`.

All dependencies are installed at build time, and all source files are copied to `INSTALL_PATH`. Nonetheless, the `docker-entrypoint.sh` script still does a thing or two depending of whether it is the first run or not. If it's the first time, it will run the `install-core.sh` and `install-web.sh` files, which will set up, among other things, the HTTPS or HTTP server, depending of the presence/absence of the SSL files required to deploy a HTTPS server.

## Docker compose

The `docker-compose.yml` file is pretty self explanatory and includes some useful comments. However, the following table aims to clarify some aspects about the options chosen to run the container:

| Option | Explanation |
|-|-|
| `network_mode: host` | In order to apply the iptables rules inside the host, we need to run the container using this network mode. |
| `NET_ADMIN` | Capability needed to interact with the network stack. |
| `NET_RAW` | Capability needed to perform operations related to network packages at kernel level. |

# Expected behaviour

Because of the options used to run the container and explained before, when the firewall rules are applied, they are still enabled even though the docker container is shutted down. However, unless theses rules are saved and automatically restored at boot time, they will not be enabled after the host machine is rebooted. 

So, you can expect the same behaviour as when using `iptables` directly from the host, with the only difference that you won't be able to see the container's rules from the host via `iptables -L`. You would have to run the command **inside** the container, via `docker exec <container_name> <command>`. Hence, to see all NAT rules inside your easywall container, you could do `docker exec easywall iptables -t nat -L`.

# Known issues

None.