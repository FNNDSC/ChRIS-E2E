#!/usr/bin/env bash

KEY=$1
SIZE=$2
TYPE=$3

# Creates files of a specified size in /tmp using the dd command

echo "filing"
dd if=/dev/zero of=/tmp/$TYPE/$KEY.txt count=1048576 bs=$SIZE
