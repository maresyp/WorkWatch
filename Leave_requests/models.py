import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Leave_request(models.Model):
    STATUS_CHOICES = [
        ('1', 'Oczekiwanie na rozpatrzenie'),
        ('2', 'Zaakceptowany'),
        ('3', 'Odrzucony'),
    ]

    LEAVE_TYPE_CHOICES = [
        ('1', 'Urlop wypoczynkowy'),
        ('2', 'Urlop na żądanie'),
        ('3', 'Urlop opiekuńczy'),
        ('4', 'Urlop z powodu siły wyższej'),
    ]

    id = models.UUIDField(default = uuid.uuid4, unique=True, primary_key=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='1')
    leave_type = models.CharField(max_length=1, choices=LEAVE_TYPE_CHOICES, default='1')
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()

    def __str__(self) -> str:
        return str(self.user)