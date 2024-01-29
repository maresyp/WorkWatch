import uuid
from datetime import UTC, datetime, timedelta

from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.models import User
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
    first_weekday_of_month = datetime(year=schedule_date.year, month=schedule_date.month, day=1, tzinfo=UTC).weekday()

    #List of the empty days at the beggining of the html grid
    blank_days = [''] * ((first_weekday_of_month) % 7)

    context['blank_days'] = blank_days

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

def navigate_to_schedule(user: User, schedule_id: uuid.UUID, direction: str) -> Schedule | None:
    current_schedule = get_object_or_404(Schedule, id=schedule_id)

    if direction == 'next':
        date = current_schedule.date + relativedelta(months=1)
    elif direction == 'previous':
        date = current_schedule.date - relativedelta(months=1)
    else:
        msg = "Invalid direction"
        raise Http404(msg)

    return Schedule.objects.filter(
        Q(user=user)
        & Q(date__month=date.month)
        & Q(date__year=date.year)).first()

@non_manager_required()
def user_schedule_navigation(request, schedule: uuid.UUID, direction: str) -> HttpResponse:

    next_schedule = navigate_to_schedule(request.user, schedule, direction)

    if not next_schedule:
        messages.error(
            request,
            f"Harmonogram dla {'następnego' if direction=='next' else 'poprzedniego'} miesiąca jeszcze nie istnieje.")
        return redirect('user_schedule', schedule=schedule)

    if (next_schedule.user != request.user):
        raise PermissionDenied
    return redirect('user_schedule', schedule=next_schedule.id)

@manager_required()
def manager_schedules(
    request,
    user_id: int | None = None,
    schedule_id: uuid.UUID | None = None,
    direction: str | None = None,
    ) -> HttpResponse:
    context: dict = {
        'users': None,
        'selected_user': None,
        'schedule': None,
        'profile': None,
    }

    context['users'] = User.objects.exclude(groups__name="Managers")
    current_date: datetime = datetime.now(tz=UTC)

    if user_id is None: # Assign default values for context
        context['selected_user'] = context['users'].first()
        context['profile'] = context['users'].first().profile

        # get schedule for current user for current month
        context['schedule'] = Schedule.objects.filter(
            Q(user=context['users'].first())
            & Q(date__month=current_date.month)
            & Q(date__year=current_date.year)).first()

        return render(request, 'schedules/manager_schedules.html', context=context)

    context['selected_user'] = context['users'].filter(id=user_id).first()
    context['schedule'] = Schedule.objects.filter(
        Q(user=context['selected_user'])
        & Q(date__month=current_date.month)
        & Q(date__year=current_date.year)).first()
    context['profile'] = context['selected_user'].profile

    if direction is not None:
        next_schedule = navigate_to_schedule(context['selected_user'], schedule_id, direction)
        if direction == 'previous' and next_schedule is None:
            messages.error(request, "Brak poprzedzającego harmonogramu")
        else:
            context['schedule'] = next_schedule

    return render(request, 'schedules/manager_schedules.html', context=context)
