from django.shortcuts import render

from WorkWatch.decorators import manager_required, non_manager_required


# Create your views here.
@non_manager_required()
def user_schedule(request):
    return render(request, 'schedules/user_schedule.html')

@manager_required()
def manager_schedules(request):
    return render(request, 'schedules/manager_schedules.html')
