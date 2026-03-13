import io
import re

from pandas import read_excel

from common.logging import logger
from database.models import UserRecord
from skud.backend import Users
from .session import PrimeSkudWebSession


class PrimeSkudWebLoader:
  def __init__(self, session: PrimeSkudWebSession, users: Users):
    self._session = session
    self._users = users

  async def update_users(self):
    logger.info(f'Downloading users list')
    try:
      xls_contents = await self._session.download_users_list()
    except Exception as e:
      logger.error(f'Failed to download users list: {e}')
      return

    data_stream = io.BytesIO(xls_contents)
    users_list = read_excel(data_stream, dtype=str, na_filter=False).to_dict(orient='records')
    logger.info(f'Users list contains {len(users_list)} records')

    user_records = []
    for row in users_list:
      name = row['Абонент']
      comment = row['Примечание абонента']

      phone = self.__normalize_phone(row['Идентификатор'])
      number_plates = self.__extract_number_plates(row['Комментарий'])
      number_plates = number_plates if number_plates else [None]

      for number_plate in number_plates:
        user_records.append(UserRecord(
          name=name, 
          comment=comment, 
          phone=phone, 
          number_plate=number_plate))

    logger.info(f'Constructed {len(user_records)} user records')
    await self._users.save_users(user_records)


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

