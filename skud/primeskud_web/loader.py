import asyncio
import io
import re
from datetime import datetime
from itertools import chain
from typing import Generator
from zoneinfo import ZoneInfo

from pandas import read_excel, read_html

from common import TZ
from common.logging import logger
from database.models import UserRecord
from database.models.access_event import AccessEvent
from skud.backend import Access, Users
from . import ACCESS_PAGES_LIMIT
from .session import PrimeSkudWebSession


class PrimeSkudWebLoader:
  def __init__(self, session: PrimeSkudWebSession, access: Access, users: Users):
    self._session = session
    self._access = access
    self._users = users

  async def update_users(self):
    try:
      logger.info(f'Downloading users list')

      xls_contents = await self._session.download_users_list()
      users_list = await asyncio.to_thread(self.__read_excel, xls_contents)

      logger.info(f'Users list contains {len(users_list)} records')

      user_records = list(chain.from_iterable([self.__user_records(row) for row in users_list]))

      logger.info(f'Constructed {len(user_records)} user records')
      await self._users.save_users(user_records)

    except Exception as e:
      logger.error(f'Failed to update users list: {e}') 
      # Do not fail if we received something weird from the server
      # We don't want to restart container endlessly
      # We'll better just retry on the next iteration


  async def update_access_events(self):
    try:
      last_event_timestamp = await self._access.get_last_access_event_timestamp()
      if last_event_timestamp:
        logger.info(f'Fetching access events after {last_event_timestamp:%Y-%m-%d %H:%M:%S}')
      else:
        logger.info(f'Fetching access events')

      page = 0
      access_events = []
      for page in range(ACCESS_PAGES_LIMIT):
        new_access_events = await self.__fetch_access_events_from_page(page)
        logger.info(f'Parsed {len(new_access_events)} access events from page #{page+1}')
        access_events.extend(new_access_events)
        if access_events and last_event_timestamp and \
                access_events[-1].timestamp <= last_event_timestamp:
          logger.info('Reached already known access events, stopping')
          break

      if last_event_timestamp:
        access_events = [event for event in access_events if event.timestamp > last_event_timestamp]

      if access_events:
        await self._access.save_access_events(access_events)

    except Exception as e:
      logger.error(f'Failed to update access events: {e}')
      # Do not fail if we received something weird from the server
      # We don't want to restart container endlessly
      # We'll better just retry on the next iteration


  def __read_excel(self, xls_contents: bytes) -> list[dict]:
    data_stream = io.BytesIO(xls_contents)
    return read_excel(data_stream, dtype=str, na_filter=False).to_dict(orient='records')
  

  def __read_html(self, html_contents: str) -> list[dict]:
    data_stream = io.StringIO(html_contents)
    return read_html(data_stream, flavor='html5lib')[0].to_dict(orient='records')


  def __user_records(self, row: dict) -> Generator[UserRecord]:
    name = row['Абонент']
    comment = row['Примечание абонента']

    phone = self.__normalize_phone(row['Идентификатор'])
    number_plates = self.__extract_number_plates(row['Комментарий'])

    for number_plate in number_plates if number_plates else [None]:
      yield UserRecord(
        name=name, 
        comment=comment, 
        phone=phone, 
        number_plate=number_plate)


  __NON_DIGITS = re.compile(r'\D')
  __LEADING_7_8 = re.compile(r'^[78]')
  
  def __normalize_phone(self, phone: str) -> str | None:
    phone = phone.strip()
    phone = re.sub(self.__NON_DIGITS, '', phone)
    phone = re.sub(self.__LEADING_7_8, '', phone)
    return '7' + phone if len(phone) == 10 else None


  __RU_LETTERS = 'ABEKMHOPCTYX'
  __RU_PATTERN = re.compile(rf'[{__RU_LETTERS}]\s*\d{{3}}\s*[{__RU_LETTERS}]{{2}}\s*\d{{2,3}}')

  def __extract_number_plates(self, number_plates: str) -> list[str]:
    number_plates = number_plates.strip().upper()
    number_plates = number_plates \
      .replace('А', 'A').replace('В', 'B').replace('Е', 'E').replace('К', 'K') \
      .replace('М', 'M').replace('Н', 'H').replace('О', 'O').replace('Р', 'P') \
      .replace('С', 'C').replace('Т', 'T').replace('У', 'Y').replace('Х', 'X')
    
    return [plate.replace(' ', '') for plate in re.findall(self.__RU_PATTERN, number_plates)]


  async def __fetch_access_events_from_page(self, page: int) -> list[AccessEvent]:
    access_events_text = await self._session.fetch_access_events(page)
    access_events_html = self.__extract_html(access_events_text)
    access_events_table = f'<table>{access_events_html}</table>'
    access_event_rows = await asyncio.to_thread(self.__read_html, access_events_table)
    return list(self.__access_events(access_event_rows))


  __JS_START = re.compile(r'^.*?(?=<tr>)', re.DOTALL)
  __JS_END = re.compile(r'(?<=</tr>)(?!.*</tr>).*$', re.DOTALL)

  def __extract_html(self, html: str) -> str:
    html = re.sub(self.__JS_START, '', html)
    html = re.sub(self.__JS_END, '', html)
    return html


  def __access_events(self, rows: list[dict[int, str]]) -> Generator[AccessEvent]:
    for row in rows:
      access_event = self.__access_event(row)
      if access_event:
        yield access_event


  __PHONE_PREFIX = re.compile(r'^Тел.\s+\+', re.IGNORECASE)
  __PHONE_REJECTED_SUFFIX = re.compile(r'\s+\(отказ\)\s*$', re.IGNORECASE)

  __ALL_NUMBERS = re.compile(r'^\d+$')
  __AFTER_COMMA = re.compile(r',.*$')

  def __access_event(self, row: dict[int, str]) -> AccessEvent | None:
    phone = re.sub(self.__PHONE_PREFIX, '', row[3])
    success = not re.search(self.__PHONE_REJECTED_SUFFIX, phone)
    phone = re.sub(self.__PHONE_REJECTED_SUFFIX, '', phone)

    if len(set(row.values())) == 1:
      # A section header row with date, not an access event
      return None

    if not re.match(self.__ALL_NUMBERS, phone):
      logger.warning(f"Unexpected phone format in access event: '{phone}', raw: '{row[3]}'")
      return None

    try:
      timestamp = datetime.strptime(row[0], '%d.%m.%Y %H:%M:%S').replace(tzinfo=ZoneInfo(TZ))
    except ValueError:
      logger.warning(f"Unexpected timestamp format in access event: '{row[0]}'")
      return None
    
    gate = re.sub(self.__AFTER_COMMA, '', row[1])

    return AccessEvent(timestamp=timestamp, phone=phone, gate=gate, success=success)
