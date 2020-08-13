#!/usr/bin/env bash

SERVICE_PS=$(pgrep "$1")
CLEAR_FILE=$(> /tmp/"$1".log)
eval $CLEAR_FILE

top -p "${SERVICE_PS}" -d 0.2 -b | awk '{print $9, $10}' >> /tmp/"${1}".log &
