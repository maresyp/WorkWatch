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
from django.utils.timezone import make_aware, now
from django.db import transaction

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
def manager_schedules(request, user_id: int | None = None, direction: str | None = None, date_str: str | None = None) -> HttpResponse:
    current_date = datetime.now(tz=UTC)
    context = {
        'users': User.objects.exclude(groups__name="Managers"),
        'selected_user': None,
        'schedule': None,
        'profile': None,
        'blank_days': [],
        'schedule_display': None,
        'displayed_date': current_date,
    }

    if user_id is not None:
        selected_user = User.objects.filter(id=user_id).first()
        if selected_user:
            context['selected_user'] = selected_user
            context['profile'] = selected_user.profile

            if date_str:
                displayed_date = datetime.strptime(date_str, '%Y-%m').replace(tzinfo=UTC)
            else:
                displayed_date = current_date

            if direction == 'next':
                displayed_date += relativedelta(months=1)
            elif direction == 'previous':
                displayed_date -= relativedelta(months=1)

            schedule = Schedule.objects.filter(
                user=selected_user, 
                date__month=displayed_date.month, 
                date__year=displayed_date.year
            ).first()

            if schedule:
                context.update(prepare_schedule_info(selected_user, schedule_id=schedule.id))
            else:
                context['displayed_date'] = displayed_date
        else:
            messages.error(request, "Nie znaleziono wybranego użytkownika.")
    else:
        # Domyślne wartości, gdy nie jest wybrany żaden użytkownik
        default_user = context['users'].first()
        context.update({
            'selected_user': default_user,
            'profile': default_user.profile,
            'schedule': prepare_schedule_info(default_user, schedule_id=None)['schedule']
        })

    return render(request, 'schedules/manager_schedules.html', context=context)

@manager_required()
def create_schedule(request, user_id, date_str):
    # Konwersja date_str na obiekt datetime
    schedule_date = datetime.strptime(date_str, '%Y-%m')
    schedule_date = make_aware(schedule_date)  # Ustawienie strefy czasowej

    # Walidacja, czy data nie jest w przeszłości
    current_date = now()
    if schedule_date.year < current_date.year or (schedule_date.year == current_date.year and schedule_date.month < current_date.month):
        messages.error(request, "Nie można utworzyć harmonogramu na miesiące, które już minęły.")
        return redirect('manager_schedules', user_id=user_id)

    # Pobranie użytkownika
    user = get_object_or_404(User, id=user_id)

    # Sprawdzenie, czy harmonogram już istnieje
    existing_schedule = Schedule.objects.filter(user=user, date__year=schedule_date.year, date__month=schedule_date.month).first()
    if existing_schedule:
        messages.error(request, "Harmonogram dla tego użytkownika i miesiąca już istnieje.")
        return redirect('manager_schedules', user_id=user_id)

   # Tworzenie nowego harmonogramu
    new_schedule = Schedule(user=user, date=schedule_date)
    new_schedule.save()

    messages.success(request, "Nowy harmonogram został utworzony.")

    # Przekierowanie do widoku manager_schedules z utworzonym miesiącem
    return redirect('manager_schedules_nav', user_id=user_id, direction='none', date_str=date_str)



@manager_required()
def update_schedule(request, user_id, date_str):
    if request.method == 'POST':
        selected_user = get_object_or_404(User, id=user_id)
        profile = selected_user.profile
        schedule_date = datetime.strptime(date_str, '%Y-%m')
        schedule_date = make_aware(schedule_date)

        work_hours_start = 8
        work_hours_end = 20
        required_hours = 4 if profile.contract_type == '2' else 8

        try:
            with transaction.atomic():
                # Znajdź lub utwórz obiekt Schedule dla danego użytkownika i daty
                schedule, created = Schedule.objects.get_or_create(
                    user=selected_user,
                    date__year=schedule_date.year,
                    date__month=schedule_date.month,
                    defaults={'date': schedule_date}
                )

                # Iteruj przez dni miesiąca i zapisuj godziny pracy
                for key, value in request.POST.items():
                    if 'start_hour_' in key:
                        day_str = key.split('_')[2]
                        start_hour_str = request.POST.get(key, '')
                        end_hour_str = request.POST.get(f'end_hour_{day_str}', '')

                        if not start_hour_str or not end_hour_str:
                            continue

                        start_hour = int(start_hour_str)
                        end_hour = int(end_hour_str)

                        if start_hour < work_hours_start or end_hour > work_hours_end:
                            raise ValueError(f"Godziny pracy muszą być między {work_hours_start}:00 a {work_hours_end}:00.")

                        work_duration = end_hour - start_hour
                        if work_duration != required_hours:
                            raise ValueError(f"Pracownik musi pracować {required_hours} godzin.")

                        day = int(day_str[6:8])  # Dzień w formacie 'Ymd'
                        start_time = datetime(schedule_date.year, schedule_date.month, day, start_hour)
                        end_time = datetime(schedule_date.year, schedule_date.month, day, end_hour)

                        ScheduleDay.objects.update_or_create(
                            schedule=schedule,
                            start_time=start_time,
                            defaults={'end_time': end_time}
                        )

                messages.success(request, "Harmonogram został zaktualizowany.")
                
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('manager_schedules_nav', user_id=user_id, direction='none', date_str=date_str)

    return Http404
