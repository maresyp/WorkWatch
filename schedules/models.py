import uuid

from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False)

    def __str__(self):
        return f"schedule for {self.user}"


class ScheduleDay(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey('schedules.Schedule', on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=False)

    def __str__(self):
        return f"{self.start_time} for {self.schedule}"
