from tortoise.models import Model
from tortoise import fields

class Detection(Model):
  class Meta:
    table="detections"
    indexes=("number_plate", "timestamp")

  id = fields.UUIDField(primary_key=True)
  timestamp = fields.DatetimeField(null=False, db_index=True)
  number_plate = fields.CharField(max_length=16, null=False, db_index=True)
  region = fields.CharField(max_length=4, null=False)
  box = fields.CharField(max_length=128, null=True)
  camera = fields.CharField(max_length=32, null=False)
  image = fields.CharField(max_length=128, null=False)
