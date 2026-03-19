from datetime import datetime
from zoneinfo import ZoneInfo

from common import TZ
from common.logging import logger
from database.models import AccessEvent


class Access:
  async def get_last_access_event_timestamp(self) -> datetime | None:
    last_event = await AccessEvent.latest('timestamp').only('timestamp')
    return last_event.timestamp if last_event else None

  async def save_access_events(self, events: list[AccessEvent]):
    unique_events = set(events)
    logger.info(f'Saving {len(unique_events)} new access events to database')
    await AccessEvent.bulk_create(unique_events)
