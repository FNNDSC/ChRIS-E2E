#!/bin/bash

# See: https://github.com/openshift/origin/issues/19141
# Issue: oc cluster down does not unmount secrets, must be done manually otherwise openshift.local.clusterup cannot be deleted

for OUTPUT in $(mount | grep openshift | awk '{ print $3}')
do
    
    echo "-----------------"
    echo $OUTPUT
    sudo umount $OUTPUT
    sudo rm -rf openshift.local.clusterup

done

