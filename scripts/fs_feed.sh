#!/usr/bin/env bash

HOST_IP=$1
JID=$2

pfurl \
                    --verb POST --raw --http ${HOST_IP}/api/v1/cmd \
                    --httpResponseBodyParse                             \
                    --jsonwrapper 'payload' --msg '
            {
    "action": "coordinate",
    "meta-compute": {
        "auid": "chris",
        "cmd": "python3 /usr/src/dircopy/dircopy.py /share/outgoing --saveinputmeta --saveoutputmeta --dir /share/incoming",
        "container": {
            "manager": {
                "app": "swarm.py",
                "env": {
                    "meta-store": "key",
                    "serviceName": "'$JID'",
                    "serviceType": "docker",
                    "shareDir": "%shareDir"
                },
                "image": "fnndsc/swarm"
            },
            "target": {
                "cmdParse": false,
                "execshell": "python3",
                "image": "fnndsc/pl-dircopy",
                "selfexec": "dircopy.py",
                "selfpath": "/usr/src/dircopy"
            }
        },
        "cpu_limit": "1000m",
        "gpu_limit": 0,
        "jid": "'$JID'",
        "memory_limit": "200Mi",
        "number_of_workers": "1",
        "service": "host",
        "threaded": true
    },
    "meta-data": {
        "localSource": {
            "path": "chris/uploads/DICOM/dataset1",
            "storageType": "swift"
        },
        "localTarget": {
            "createDir": true,
            "path": "chris/feed_1/dircopy_1/data"
        },
        "remote": {
            "key": "%meta-store"
        },
        "service": "host",
        "specialHandling": {
            "cleanup": true,
            "op": "plugin"
        },
        "transport": {
            "compress": {
                "archive": "zip",
                "cleanup": true,
                "unpack": true
            },
            "mechanism": "compress"
        }
    },
    "meta-store": {
        "key": "jid",
        "meta": "meta-compute"
    },
    "threadAction": true
} ' --quiet --jsonpprintindent 4
