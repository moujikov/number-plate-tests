#!/usr/bin/env bash

source .venv/bin/activate

export DATABASE_TYPE=postgres
export DATABASE_HOST=any
export DATABASE_PORT=1000
export DATABASE_NAME=any
export DATABASE_USER=any
export DATABASE_PASSWORD=any

python -m database print_schema

deactivate
