import sys

from tortoise import Tortoise, run_async
from tortoise.utils import get_schema_sql

from . import init_database, release_database

async def print_schema():
  await init_database()
  schemas = get_schema_sql(Tortoise.get_connection('default'), safe=False)
  print(schemas)


if sys.argv[1] == 'print_schema':
  print('------------ DATABASE SCHEMA ------------')

  try:
    run_async(print_schema())
  finally:
    run_async(release_database())
