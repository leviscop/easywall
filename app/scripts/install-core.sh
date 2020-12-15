#!/bin/bash

CONFIGFOLDER="config"
CONFIGFILE="easywall.ini"
SAMPLEFILE="easywall.sample.ini"
CONFIGFILELOG="log.ini"
SAMPLEFILELOG="log.sample.ini"

SCRIPTNAME=$(basename "$0")
SCRIPTSPATH=$(dirname "$(readlink -f "$0")")
HOMEPATH="$(dirname "$SCRIPTSPATH")"

if [ "$EUID" -ne 0 ]; then
    read -r -d '' NOROOT <<EOF
To install easywall, you need administration rights.
You can use the following commands:

# sudo -H bash ${SCRIPTSPATH}/${SCRIPTNAME}
or
# su root -c "${SCRIPTSPATH}/${SCRIPTNAME}"
EOF
    echo "$NOROOT"
    exit 1
fi

# Step 1
echo "" && echo -e "\\e[33m($STEP/$STEPS)\\e[32m Create the configuration from the example configuration \\e[39m" && ((STEP++))
if [ -f "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILE}" ]; then
    echo -e "\\e[33mThe configuration file is not overwritten because it already exists and adjustments may have been made.\\e[39m"
else
    cp -v "${HOMEPATH}/${CONFIGFOLDER}/${SAMPLEFILE}" "${HOMEPATH}/${CONFIGFOLDER}/${CONFIGFILE}"
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
You have successfully installed the easywall core on your Linux system.

For the next steps, please follow our installation instructions on GitHub.
https://github.com/jpylypiw/easywall/blob/master/docs/INSTALL.md

Daemon Status:

EOF
echo -e "${INTRODUCTION}"
