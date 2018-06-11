#!/bin/bash

rm /home/ckaubisch/.kube/config
oc login https://openshift.massopen.cloud --token=hZzVgAH_zgLfWKqWZUMduzp8Qrs0_NpukAupJh20nuk
oc project chris-scale
oc delete secret kubecfg
oc create secret generic kubecfg --from-file=/home/ckaubisch/.kube/config -n chris-scale
#oc new-app /home/ckaubisch/pman/openshift/pman-openshift-template.json
oc new-app pman-openshift-template-without-reaper.json
oc new-app /home/ckaubisch/pfioh/openshift/pfioh-openshift-template.json
