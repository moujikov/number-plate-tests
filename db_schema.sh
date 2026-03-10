#!/usr/bin/env bash

source .venv/bin/activate

export DATABASE_URL='postgres://_:_@_:5432/__'
python -m database print_schema

deactivate
