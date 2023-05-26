#!/bin/sh

cd /usr/src/app
python ./docker/server/pre_start.py
python ./init_db.py
exec python ./server.py
