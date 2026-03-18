from tortoise import fields
from tortoise.models import Model
from tortoise.indexes import Index

class DetectionEvent(Model):
  id = fields.UUIDField(primary_key=True)
  timestamp = fields.DatetimeField(null=False)
  number_plate = fields.CharField(max_length=16, null=False)
  region = fields.CharField(max_length=4, null=False)
  box = fields.CharField(max_length=128, null=True)
  camera = fields.CharField(max_length=32, null=False)
  image = fields.CharField(max_length=128, null=False)
  user = fields.ForeignKeyField('models.UserRecord', on_delete = fields.RESTRICT, null=True)
  
  class Meta:
    table="detection_events"
    indexes = [
      Index(fields=['timestamp'], name='idx_detection_events_timestamp'),
      Index(fields=['number_plate'], name='idx_detection_events_number_plate'),
      Index(fields=['number_plate','timestamp'], name='idx_detection_events_number_plate_timestamp'),
    ]
