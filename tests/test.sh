#!/bin/bash

export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=postgres
export SECRET_KEY=django-insecure-m=@g$0^4bxl&h^p8a8n^yt%rcv8qlz5(5kly(&06a0ztqcf-t7
python3 manage.py test $1