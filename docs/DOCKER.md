# How to *dockerize* Easywall

Until an official image is uploaded to Docker Hub, here's how to run Easywall inside a docker container:

1. Checkout the `docker` branch:
    ```
    git clone --single-branch --branch docker https://github.com/joseantmazonsb/easywall.git
    ```
2. Use `docker-compose` to build and run the container:
    ```
    docker-compose up -d
    ```

## Provide a secure access to the web GUI

The docker approach does not make use of any SSL features, but instead assumes the user installing the software will provide a safe way to access the web GUI. This can be easily achieved using a **reverse proxy**, as explained in the next subsection:

### Apache reverse proxy

To set up a secure reverse proxy using Apache2 you will only need to create a new configuration file for the virtual host as follows:

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

Of course, you will need to edit this template to fit your own scenario.