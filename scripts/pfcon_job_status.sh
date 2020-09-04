#!/usr/bin/env bash
HOST_IP=$1
JID=$2

pfurl --verb POST --raw \
      --http ${HOST_IP}/api/v1/cmd \
      --httpResponseBodyParse \
      --jsonwrapper 'payload' \
      --msg '
{   "action":           "status",
    "threadAction":     false,
        "meta": {
            "remote": {
                    "key":          "'$JID'"
            }
        }
}'
