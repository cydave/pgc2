#!/bin/sh

cd /usr/src/app
python ./docker/worker/pre_start.py
sleep 3
exec python ./worker.py "$@"
