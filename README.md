# Installation

Here's how to run Easywall inside a docker container.

## Docker Hub

*Planned*

## Github repository

1. Checkout the `docker` branch to obtain the most recent stable version:
    ```
    git clone --single-branch --branch docker https://github.com/joseantmazonsb/easywall.git
    ```
    Or checkout or download any other `docker` [release](https://github.com/joseantmazonsb/easywall/releases) (they are tagged as `vX.X.X-docker`).

2. Use `docker-compose` to build and run the container:
    ```
	cd ./easywall
    docker-compose up -d
    ```

# Expected behaviour

The container will load all rules from the file `rules.yml` when it is started, and will be enabled until the host is rebooted, even if the container is stopped. Furthermore, **the container won't start at boot time by default**, so unless the `restart` option is modified inside the `docker-compose.yml` file, the rules will not be enabled after the host machine is rebooted. This way, we achieve the same behaviour as if running iptables directly over the host.

Moreover, you will be able to see the firewall rules from the host via `iptables -L`, although you can also use `docker exec <container_name> <command>` to execute all sort of commands inside the container.

*Note: the port running the easywall's web GUI will always be automatically open on start, and its tagged as `easywall-web`.*

# Security concerns

The docker approach lets you choose whether to start the web server with SSL features enabled or not.

## Running a HTTPS server inside the container

By default, the container will only run a HTTPS server if a SSL certificate and key are provided within the `docker-compose.yaml` file. You will need to mount both files as volumes the first time you run `docker-compose up` if you want a HTTPS server deployed by default. However, if you don't, you still can switch to HTTPS directly from the web GUI, via `Options -> Webinterface`.

The SSL files must be placed inside the container under `/ssl`, and the certficate must be named `easywall.crt`, while the private key must be named `easywall.key`.

## Reverse proxy

If you already have a main web server running in another machine with SSL features enabled, and you would like to reuse it, then the reverse proxy's approach is your best option.

To set up a secure reverse proxy using Apache2 you will only need to create a configuration file for the virtual host as follows:

```apache
<VirtualHost *:443>
	ServerName easywall.example.com
	ServerAlias easywall.example.com
	ServerAdmin hostmaster@example.com

	ErrorLog ${APACHE_LOG_DIR}/error.log
	CustomLog ${APACHE_LOG_DIR}/access.log combined

	ProxyPreserveHost On
	ProxyPass / http://10.0.0.99:12227/
	ProxyPassReverse / http://10.0.0.99:12227/

	SSLEngine on
	SSLCertificateFile /certs/fullchain
	SSLCertificateKeyFile /certs/privkey
</VirtualHost>
```

And, of course, you will need to edit this template to fit your own scenario.

# Logging

By default, Easywall logs to `/var/log/easywall.log` inside the container. So, you could create a log file and mount it as a volume pointing to `/var/log/easywall.log`, and you would then be able to access Easywall's logs directly from the host.

Moreover, you may also call `docker logs <container_name>` to check the logs from the current execution.

# Known issues

## I switched from HTTPS to HTTP and I can no longer log in

This is a cookie 'issue'. You will need to remove all easywall cookies from your browser and it should be working as expected again.

## I can't see my rules

It is possible that easywall rules are not displayed by running `iptables` directly from the host. If that ever happens, running the command inside the container (`docker exec iptables <options>`) should display them.