#!/bin/bash

export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=postgres
export SECRET_KEY=h*c#0cq8$lvp_el8l7h(g_n-5^bmt9b#_kci%d05hhh3u-_=j*
python3 manage.py test $1