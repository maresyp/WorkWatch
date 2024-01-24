import uuid
from datetime import UTC, datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.formats import date_format

from Leave_requests.models import Leave_request
from WorkWatch.decorators import manager_required, non_manager_required

from .models import Schedule, ScheduleDay


def prepare_schedule_info(user, schedule_id: uuid.UUID | None = None) -> dict:
    context: dict = {
        'schedule': None,
        'schedule_display': None,
    }

    if not schedule_id:
        # get schedule for current user for current month
        date: datetime = datetime.now(tz=UTC)
        schedule = Schedule.objects.filter(
            Q(user=user)
            & Q(date__month=date.month)
            & Q(date__year=date.year))
    else:
        schedule = Schedule.objects.filter(id=schedule_id)

    schedule = schedule.first()
    if not schedule: # early return if no schedule exists for given month
        return context

    schedule_date = schedule.date
    # Get the last day of the current month
    last_day = (schedule_date.replace(month=schedule_date.month+1, day=1) - timedelta(days=1)).day
    schedule_display = {
        date: {
            'weekday': date_format(date, 'l', use_l10n=True),
            'start_time': None,
            'end_time': None,
            'on_leave': False}
        for date in [datetime(year=schedule_date.year, month=schedule_date.month, day=i, tzinfo=UTC) for i in range(1, last_day+1)]
        }

    scheduled_days = ScheduleDay.objects.filter(schedule=schedule)
    for date in schedule_display:
        for day in scheduled_days:
            if day.start_time.day == date.day:
                schedule_display[date]['start_time'] = day.start_time
                schedule_display[date]['end_time'] = day.end_time

    leaves = Leave_request.objects.filter(
        Q(user=user)
        & Q(start_date__month=schedule_date.month)
        & Q(start_date__year=schedule_date.year)
        & Q(status='2'))

    for leave in leaves:
        for date in schedule_display:
            if leave.start_date.day <= date.day <= leave.end_date.day:
                schedule_display[date]['on_leave'] = True

    context['schedule'] = schedule
    context['schedule_display'] = schedule_display
    return context

# Create your views here.
@non_manager_required()
def user_schedule(request, schedule: uuid.UUID | None = None) -> HttpResponse:
    context = prepare_schedule_info(request.user, schedule_id=schedule)
    return render(request, 'schedules/user_schedule.html', context=context)

@non_manager_required()
def user_schedule_navigation(request, schedule: uuid.UUID, direction: str) -> HttpResponse:
    current_schedule = get_object_or_404(Schedule, id=schedule)
    if (current_schedule.user != request.user):
        raise PermissionDenied

    if direction == 'next':
        date = current_schedule.date + relativedelta(months=1)
    elif direction == 'previous':
        date = current_schedule.date - relativedelta(months=1)
    else:
        msg = "Invalid direction"
        raise Http404(msg)

    next_schedule = Schedule.objects.filter(
        Q(user=request.user)
        & Q(date__month=date.month)
        & Q(date__year=date.year)).first()

    if not next_schedule:
        messages.error(request, f"Harmonogram dla {date.strftime('%m-%Y')} jeszcze nie istnieje.")
        return redirect('user_schedule', schedule=current_schedule.id)

    return redirect('user_schedule', schedule=next_schedule.id)

@non_manager_required()
def user_schedule_from_calendar(request, date: datetime):
    pass

@manager_required()
def manager_schedules(request) -> HttpResponse:
    return render(request, 'schedules/manager_schedules.html')
