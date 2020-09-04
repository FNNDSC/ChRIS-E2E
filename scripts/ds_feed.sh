#!/usr/bin/env bash

HOST_IP=$1
JID=$2
FILE_NAME=$3

# shellcheck disable=SC2016
pfurl --verb POST --raw --http ${HOST_IP}/api/v1/cmd \
      --httpResponseBodyParse --jsonwrapper 'payload'     \
      --msg '
        {   "action": "coordinate",
            "threadAction":     true,
            "meta-store": {
                        "meta":         "meta-compute",
                        "key":          "jid"
            },

            "meta-data": {
                "remote": {
                        "key":          "%meta-store"
                },
                "localSource": {
                        "path":         "chris/feed_1/dircopy_1/data",
                        "storageType":  "swift"
                },
                "localTarget": {
                        "path":         "chris/feed_1/med2img_'$JID'/data",
                        "createDir":    true
                },
                "specialHandling": {
                        "op":           "plugin",
                        "cleanup":      true
                },
                "transport": {
                    "mechanism":    "compress",
                    "compress": {
                        "encoding": "none",
                        "archive":  "zip",
                        "unpack":   true,
                        "cleanup":  true
                    }
                },
                "service":              "host"
            },

            "meta-compute":  {
                "cmd":      "python3 /usr/src/med2img/med2img.py --outputFileType jpg --sliceToConvert -1 --func invertIntensities /share/incoming /share/outgoing -i '$FILE_NAME' -o sample'$JID'.png",
                "auid":     "rudolphpienaar",
                "jid":      "'$JID'",
                "threaded": true,
                "container":   {
                        "target": {
                            "image":            "fnndsc/pl-med2img",
                            "cmdParse":         true
                        },
                        "manager": {
                            "image":            "fnndsc/swarm",
                            "app":              "swarm.py",
                            "env":  {
                                "meta-store":   "key",
                                "serviceType":  "docker",
                                "shareDir":     "%shareDir",
                                "serviceName":  "'$JID'"
                            }
                        }
                },
                "service":              "host"
            }
        }
'

