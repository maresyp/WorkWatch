from datetime import UTC, datetime, timedelta

from django.db.models import Q
from django.shortcuts import render

from Leave_requests.models import Leave_request
from WorkWatch.decorators import manager_required, non_manager_required

from .models import Schedule, ScheduleDay


# Create your views here.
@non_manager_required()
def user_schedule(request):
    current_date: datetime = datetime.now(tz=UTC)

    # get schedule for current user for current month
    schedule = Schedule.objects.filter(
        Q(user=request.user)
        & Q(date__month=current_date.month)
        & Q(date__year=current_date.year))

    if not schedule: # early return if no schedule exists for given month
        return render(request, 'schedules/user_schedule.html', context={'schedule': None})


    # Get the last day of the current month
    last_day = (current_date.replace(month=current_date.month+1, day=1) - timedelta(days=1)).day
    schedule_display = {
        date: {
            'weekday': date.strftime('%A'),
            'start_time': None,
            'end_time': None,
            'on_leave': False}
        for date in [datetime(year=current_date.year, month=current_date.month, day=i, tzinfo=UTC) for i in range(1, last_day+1)]
        }

    scheduled_days = ScheduleDay.objects.filter(schedule=schedule[0])
    for date in schedule_display:
        for day in scheduled_days:
            if day.start_time.day == date.day:
                schedule_display[date]['start_time'] = day.start_time
                schedule_display[date]['end_time'] = day.end_time

    leaves = Leave_request.objects.filter(
        Q(user=request.user)
        & Q(start_date__month=current_date.month)
        & Q(start_date__year=current_date.year)
        & Q(status='2'),
        )

    for leave in leaves:
        for date in schedule_display:
            if leave.start_date.day <= date.day <= leave.end_date.day:
                schedule_display[date]['on_leave'] = True

    context: dict = {
        'schedule': schedule_display,
    }
    return render(request, 'schedules/user_schedule.html', context=context)

@manager_required()
def manager_schedules(request):
    return render(request, 'schedules/manager_schedules.html')
