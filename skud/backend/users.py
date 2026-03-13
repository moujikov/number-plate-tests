from datetime import datetime
from zoneinfo import ZoneInfo

from common import TZ
from common.logging import logger
from database.models import UserRecord


class Users:
  async def save_users(self, users: list[UserRecord]):
    filter = UserRecord.filter(removed__isnull=True)
    new_users = set(users)
    existing_users = set(await filter.all())
    
    users_to_remove = existing_users - new_users
    if users_to_remove:
      for user in users_to_remove:
        user.removed = datetime.now(tz = ZoneInfo(TZ))
      logger.info(f'Marking {len(users_to_remove)} removed user records in database')
      await UserRecord.bulk_update(users_to_remove, fields=['removed'])

    users_to_add = new_users - existing_users
    if users_to_add:
      logger.info(f'Adding {len(users_to_add)} new user records to database')
      await UserRecord.bulk_create(users_to_add)

    if users_to_remove or users_to_add:
      logger.info(f'Total {len(users_to_add) + len(users_to_remove)} user records persisted')
    else:
      logger.info(f'No changes in user records')
