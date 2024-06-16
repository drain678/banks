#!/bin/bash

export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432
export POSTGRES_USER=test
export POSTGRES_PASSWORD=test
export POSTGRES_DB=postgres
export SECRET_KEY=1grz2o3i$fh+r9mxr_5hn*2#&qf5bf=c6fk^j$0pw3&5q5zzz5
python3 manage.py test $1