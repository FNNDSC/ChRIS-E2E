#!/usr/bin/env bash


# Based on path given in config file, read from swift-credentials
# Obtain a list of all objects in swift storage

# use config parser

. config.cfg

CMD=$1
O_PATH=$PATH

PATH=$SWIFT_PATH'/swift-credentials.cfg' 

OIFS=$IFS;
IFS=" ";
OS_AUTH_URL=""
USERNAME=""
PASSWORD=""
OS_PROJECT_DOMAIN=""
OS_PROJECT_NAME=""

DONE=false

until $DONE ; do
    read line || DONE=true

    #echo $line

    #if [[ "$line" == "[ConfigInfo]" ]]; then
    #    echo "THIS IS CONFIGINFO"
    #fi
    
    IFS="="
    words=( $line )
    key="${words[0]}"
    val="${words[1]}"

    cleankey="$(echo ${key//[[:blank:]]/})"

    if [[ "$cleankey" == "osAuthUrl" ]]; then
	OS_AUTH_URL=$val
    elif [[ "$cleankey" == "username" ]]; then
	USERNAME=$val
    elif [[ "$cleankey" == "password" ]]; then
	PASSWORD=$val
    elif [[ "$cleankey" == "osProjectDomain" ]]; then
	OS_PROJECT_DOMAIN=$val
    elif [[ "$cleankey" == "osProjectName" ]]; then
	OS_PROJECT_NAME=$val
    fi

done < $PATH

PATH=$O_PATH

SWIFTLIST="swift --os-auth-url $OS_AUTH_URL --auth-version 3 --os-project-name $OS_PROJECT_NAME --os-project-domain-name $OS_PROJECT_DOMAIN --os-username $USERNAME --os-user-domain-name default --os-password $PASSWORD list"

SWIFTDEL="swift --os-auth-url $OS_AUTH_URL --auth-version 3 --os-project-name $OS_PROJECT_NAME --os-project-domain-name $OS_PROJECT_DOMAIN --os-username $USERNAME --os-user-domain-name default --os-password $PASSWORD delete --all"

if [[ "$CMD" == "list" ]]; then
    eval $SWIFTLIST
elif [[ "$CMD" == "delete" ]]; then
    eval $SWIFTDEL
else
    echo "Command not found."
fi
