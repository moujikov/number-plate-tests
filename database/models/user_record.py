from tortoise import fields
from tortoise.models import Model
from tortoise.indexes import Index

class UserRecord(Model):
  id = fields.IntField(primary_key=True)
  name = fields.CharField(max_length=128, null=False)
  comment = fields.CharField(max_length=128, null=True)
  phone = fields.CharField(max_length=16, null=True)
  number_plate = fields.CharField(max_length=16, null=True)
  added = fields.DatetimeField(auto_now_add=True, null=False)
  removed = fields.DatetimeField(auto_now_add=False, null=True)

  class Meta:
    table = "user_records"
    indexes = [
      Index(fields=['number_plate'], name='idx_user_records_number_plate'),
      Index(fields=['removed'], name='idx_user_records_removed')
    ]


  def __eq__(self, other):
    if not isinstance(other, UserRecord):
      return NotImplemented    
    return self.name == other.name and \
           self.comment == other.comment and \
           self.phone == other.phone and \
           self.number_plate == other.number_plate

  def __hash__(self):
    return hash((self.name, self.comment, self.phone, self.number_plate))
