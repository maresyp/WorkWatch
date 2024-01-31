from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Q
from WorkWatch.decorators import non_manager_required, manager_required
from schedules.models import ScheduleDay
from .models import Leave_request
from .forms import LeaveRequestForm

@non_manager_required(login_url='login')
def User_leave_requests(request):
    user = request.user
    profile = user.profile
    form = LeaveRequestForm()
    requests_history = Leave_request.objects.filter(user=user).order_by('-start_date')

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = user

            # Pobranie danych z formularza
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            leave_type = form.cleaned_data['leave_type']
            num_days_requested = (end_date - start_date).days + 1

            # Sprawdzanie dostępności dni urlopowych
            if leave_type == '1':  # Urlop wypoczynkowy
                if profile.available_leave >= num_days_requested:
                    profile.available_leave -= num_days_requested
                    if profile.available_leave < profile.on_demand_leave:
                        profile.on_demand_leave = profile.available_leave # Zaakceptowany, jeśli to urlop na żądanie
                else:
                    messages.error(request, 'Nie masz wystarczającej liczby dni urlopu wypoczynkowego.')
                    return redirect('User_leave_requests')
            elif leave_type == '2':  # Urlop na żądanie
                if profile.available_leave >= num_days_requested and profile.on_demand_leave >= num_days_requested:
                    profile.available_leave -= num_days_requested
                    profile.on_demand_leave -= num_days_requested
                    leave_request.status = '2'  # Od razu zaakceptowany
                else:
                    messages.error(request, 'Nie masz wystarczającej liczby dni urlopu na żądanie.')
                    return redirect('User_leave_requests')
            elif leave_type == '3':  # Urlop na żądanie
                if profile.parental_leave >= num_days_requested:
                    profile.parental_leave -= num_days_requested
                else:
                    messages.error(request, 'Nie masz wystarczającej liczby dni urlopu opiekuńczego.')
                    return redirect('User_leave_requests')
            elif leave_type == '4':  # Urlop na żądanie
                if profile.force_majeure_leave >= num_days_requested:
                    profile.force_majeure_leave -= num_days_requested
                else:
                    messages.error(request, 'Nie masz wystarczającej liczby dni urlopu z powodu siły wyższej.')
                    return redirect('User_leave_requests')    

            profile.save()
            leave_request.num_of_days = num_days_requested
            leave_request.save()
            messages.success(request, 'Wniosek urlopowy został złożony.')
            requests_history = Leave_request.objects.filter(user=user).order_by('-start_date')
            return redirect('User_leave_requests')

    context = {
        'form': form,
        'user': user,
        'profile': profile,
        'requests_history': requests_history,
    }
    return render(request, 'Leave_requests/user_leave_requests.html', context)

@manager_required(login_url='login')
def Manager_leave_requests(request, user_id=None):
    non_managers = User.objects.exclude(groups__name='Managers')

    users_with_pending_requests = non_managers.filter(
        leave_request__status='1'
    ).order_by('last_name', 'first_name').distinct()

    users_without_requests = non_managers.exclude(
        leave_request__status='1'
    ).order_by('last_name', 'first_name').distinct()

    selected_user = None
    profile = None
    requests_history = None
    pending_requests = None

    if user_id:
        selected_user = get_object_or_404(User, pk=user_id)
    elif users_with_pending_requests.exists():
        selected_user = users_with_pending_requests.first()
    elif users_without_requests.exists():
        selected_user = users_without_requests.first()

    if selected_user:
        profile = selected_user.profile
        requests_history = Leave_request.objects.filter(
            user=selected_user, 
            status__in=['2', '3']
        ).order_by('-start_date')
        pending_requests = Leave_request.objects.filter(
            user=selected_user, 
            status='1'
        ).order_by('start_date')

    context = {
        'users_with_pending_requests': users_with_pending_requests,
        'users_without_requests': users_without_requests,
        'profile': profile,
        'requests_history': requests_history,
        'pending_requests': pending_requests,
    }
    return render(request, 'Leave_requests/manager_leave_requests.html', context)

@manager_required(login_url='login')
def accept_leave_request(request, request_id):
    leave_request = get_object_or_404(Leave_request, pk=request_id)
    leave_request.status = '2'  # Status 'zaakceptowany'
    leave_request.save()

    # Pobierz id użytkownika wnioskującego o urlop
    user_id = leave_request.user.id

    # Usuń wszystkie ScheduleDay dla tego użytkownika, które zawierają się w zakresie dat wniosku urlopowego
    ScheduleDay.objects.filter(
        Q(schedule__user_id=user_id) &
        Q(start_time__gte=leave_request.start_date) &
        Q(end_time__lte=leave_request.end_date)
    ).delete()

    messages.success(request, 'Wniosek urlopowy został zaakceptowany.')
    return redirect('Manager_leave_requests', user_id=user_id)

@manager_required(login_url='login')
def decline_leave_request(request, request_id):
    leave_request = get_object_or_404(Leave_request, pk=request_id)
    leave_request.status = '3'  # Status 'odrzucony'
    leave_request.save()
    user_id = leave_request.user.id
    messages.error(request, 'Wniosek urlopowy został odrzucony.')
    return redirect('Manager_leave_requests', user_id=user_id)

def search_users(request):
    query = request.GET.get('query', '')
    non_managers = User.objects.exclude(groups__name='Managers')

    if query:
        results = non_managers.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        )
    else:
        results = non_managers

    # Logika do segregowania użytkowników z wnioskami i bez
    users_with_requests = results.filter(leave_request__status='1').distinct()
    users_without_requests = results.exclude(leave_request__status='1').distinct()

    data = []
    # Najpierw dodajemy użytkowników z wnioskami
    for user in users_with_requests:
        data.append(get_user_data(user, has_request=True))
    
    # Następnie resztę użytkowników
    for user in users_without_requests:
        data.append(get_user_data(user, has_request=False))

    return JsonResponse(data, safe=False)

def get_user_data(user, has_request=False):
    profile = user.profile if hasattr(user, 'profile') else None
    imageURL = profile.imageURL if profile else ''
    return {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'imageURL': imageURL,
        'id': user.id,
        'has_request': has_request  # Dodatkowe pole informujące o wniosku
    }