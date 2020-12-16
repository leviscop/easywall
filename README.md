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

The container will load all rules from the file `rules.yml` when it is started, and will be enabled until the host is rebooted, even if the container is stopped. Furthermore, **the container won't start at boot time by default**, so unless the `restart` option is modified inside the `docker-compose.yml` file, the rules will not be enabled after the host machine is rebooted. This way, we achieve the same behaviour as if running iptables directly over the host.

Moreover, you will be able to see the firewall rules from the host via `iptables -L`, although you can also use `docker exec <container_name> <command>` to execute all sort of commands inside the container.

# Known issues

- Running other containers will **slightly** affect your iptables rules, since docker will automatically add rules when starting a container.