#!/bin/bash

CONFIGFOLDER="config"
CONFIGFILE="web.ini"
SAMPLEFILE_HTTP="web.sample.ini"
SAMPLEFILE_HTTPS="web.https.sample.ini"
CONFIGFILELOG="log.ini"
SAMPLEFILELOG="log.sample.ini"
LOGFILE="/var/log/easywall.log"

SCRIPTNAME=$(basename "$0")
SCRIPTSPATH=$(dirname "$(readlink -f "$0")")
HOMEPATH="$(dirname "$SCRIPTSPATH")"
SSL_DIR="/ssl"
SSL_CRT_NAME="easywall.crt"
SSL_KEY_NAME="easywall.key"

if [ "$EUID" -ne 0 ]; then
    read -r -d '' NOROOT <<EOF
To install easywall-web, you need administration rights.
You can use the following commands:

# sudo -H bash ${SCRIPTSPATH}/${SCRIPTNAME}
or
# su root -c "${SCRIPTSPATH}/${SCRIPTNAME}"
EOF
    echo "$NOROOT"
    exit 1
fi

# Step 1
echo "" && echo -e "\\e[32m Create the configuration from the example configuration \\e[39m" && ((STEP++))
if [ -f "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILE}" ]; then
    echo -e "\\e[33mThe configuration file is not overwritten because it already exists and adjustments may have been made.\\e[39m"
else
    ssl_crt=0
    ssl_key=0
    
    if [ -f "${SSL_DIR}/${SSL_CRT_NAME}" ]; then
        ssl_crt=1
    else
        echo -e "\\e[33mSSL certificate file not found!\\e[39m"
    fi
    
    if [ -f "${SSL_DIR}/${SSL_KEY_NAME}" ]; then
        ssl_key=1
    else
        echo -e "\\e[33mSSL key file not found!\\e[39m"
    fi

    if [ $ssl_crt -eq 1 ] && [ $ssl_key ]; then
        echo -e "\\e[33mSSL files found. HTTPS will be used.\\e[39m"
        cp -v "${HOMEPATH}/${CONFIGFOLDER}/${SAMPLEFILE_HTTPS}" "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILE}"
    else
        echo -e "\\e[33mSSL files not found. HTTP will be used.\\e[39m"
        cp -v "${HOMEPATH}/${CONFIGFOLDER}/${SAMPLEFILE_HTTP}" "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILE}"
    fi
fi
if [ -f "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILELOG}" ]; then
    echo -e "\\e[33mThe log configuration file is not overwritten because it already exists and adjustments may have been made.\\e[39m"
else
    cp -v "${HOMEPATH}/${CONFIGFOLDER}/${SAMPLEFILELOG}" "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILELOG}"
fi

# Finished.
echo "" && echo ""
read -r -d '' INTRODUCTION <<EOF
\\e[33m------------------------------\\e[39m
You have successfully installed the easywall web interface.

For the next steps, please follow our installation instructions on GitHub.
https://github.com/jpylypiw/easywall/blob/master/docs/INSTALL.md

Daemon Status:

EOF
echo -e "${INTRODUCTION}"