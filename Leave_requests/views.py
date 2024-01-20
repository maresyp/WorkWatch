from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


# Create your views here.

@login_required(login_url='login')
def User_leave_requests(request):
    page = 'account'
    user = request.user
    profile = request.user.profile

    context = {
        'user': user,
        'profile': profile,
        'page': page,
    }
    return render(request, 'Leave_requests/user_leave_requests.html', context)