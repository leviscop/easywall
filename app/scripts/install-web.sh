#!/bin/bash

BOOTSTRAP="4.1.3"
FONTAWESOME="4.7.0"
JQUERY="3.3.1"
POPPER="1.14.3"
CONFIGFOLDER="config"
RULESFOLDER="rules"
CONFIGFILE="web.ini"
SAMPLEFILE_HTTP="web.sample.ini"
SAMPLEFILE_HTTPS="web.https.sample.ini"
CONFIGFILELOG="log.ini"
SAMPLEFILELOG="log.sample.ini"
SERVICEFILE="/lib/systemd/system/easywall-web.service"
SERVICEFILE_EASYWALL="/lib/systemd/system/easywall.service"
LOGFILE="/var/log/easywall.log"

SCRIPTNAME=$(basename "$0")
SCRIPTSPATH=$(dirname "$(readlink -f "$0")")
HOMEPATH="$(dirname "$SCRIPTSPATH")"
SSL_DIR="/ssl"
SSL_CRT_NAME="easywall.crt"
SSL_KEY_NAME="easywall.key"
WEBDIR="$HOMEPATH/easywall/web"
TMPDIR="$WEBDIR/tmp"

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

# Step 2
echo "" && echo -e "\\e[32m Download of several libraries required for easywall-web \\e[39m" && ((STEP++))
mkdir "$TMPDIR" && cd "$TMPDIR" || exit 1

# Bootstrap
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/css/bootstrap.min.css" && cp -v "bootstrap.min.css" "$WEBDIR/static/css/"
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/css/bootstrap.min.css.map" && cp -v "bootstrap.min.css.map" "$WEBDIR/static/css/"
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/js/bootstrap.min.js" && cp -v "bootstrap.min.js" "$WEBDIR/static/js/"
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://stackpath.bootstrapcdn.com/bootstrap/$BOOTSTRAP/js/bootstrap.min.js.map" && cp -v "bootstrap.min.js.map" "$WEBDIR/static/js/"

# Font Awesome
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://fontawesome.com/v$FONTAWESOME/assets/font-awesome-$FONTAWESOME.zip"
unzip -q "font-awesome-$FONTAWESOME.zip"
cp -rv "font-awesome-$FONTAWESOME/css/"* "$WEBDIR/static/css/"
cp -rv "font-awesome-$FONTAWESOME/fonts/"* "$WEBDIR/static/fonts/"

# JQuery Slim (for Bootstrap)
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://code.jquery.com/jquery-$JQUERY.slim.min.js" && cp -v jquery-$JQUERY.slim.min.js "$WEBDIR/static/js/"

# Popper (for Bootstrap)
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://cdnjs.cloudflare.com/ajax/libs/popper.js/$POPPER/umd/popper.min.js" && cp -v popper.min.js "$WEBDIR/static/js/"
wget -q --timeout=10 --tries=5 --retry-connrefused --show-progress "https://cdnjs.cloudflare.com/ajax/libs/popper.js/$POPPER/umd/popper.min.js.map" && cp -v popper.min.js.map "$WEBDIR/static/js/"

cd "$HOMEPATH" || exit 1
rm -rf "$TMPDIR"

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