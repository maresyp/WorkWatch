from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from datetime import datetime
from .models import Leave_request
from Users.models import Profile
from .forms import LeaveRequestForm

@login_required(login_url='login')
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
