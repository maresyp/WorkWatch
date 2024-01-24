from django.contrib import admin

from .models import Schedule, ScheduleDay

# Register your models here.

admin.site.register(Schedule)
admin.site.register(ScheduleDay)
