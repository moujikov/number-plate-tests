from tortoise import fields
from tortoise.models import Model
from tortoise.indexes import Index

class AccessEvent(Model):
  id = fields.UUIDField(primary_key=True)
  timestamp = fields.DatetimeField(null=False)
  phone = fields.CharField(max_length=16, null=False)
  gate = fields.CharField(max_length=32, null=False)
  success = fields.BooleanField(null=False)
  
  class Meta:
    table="access_events"
    indexes = [
      Index(fields=['timestamp'], name='idx_access_events_timestamp'),
      Index(fields=['phone'], name='idx_access_events_phone')
    ]

  def __eq__(self, other):
    if not isinstance(other, AccessEvent):
      return NotImplemented    
    return self.timestamp == other.timestamp and \
           self.phone == other.phone

  def __hash__(self):
    return hash((self.timestamp, self.phone))
  