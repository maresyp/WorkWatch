from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from WorkWatch.decorators import manager_required

from .forms import ChangePasswordForm, CustomUserCreationForm, ProfileCreationForm, ProfileForm


def login_user(request):
    page = 'login'

    if request.user.is_authenticated:
        if request.user.groups.filter(name='Managers').exists():
            return redirect('Manager_leave_requests')
        else:
            return redirect('User_leave_requests')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except Exception:
            messages.error(request, 'Nie istnieje użytkownik o podanej nazwie.')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.groups.filter(name='Managers').exists():
                return redirect(request.GET['next'] if 'next' in request.GET else 'Manager_leave_requests')
            else:
                return redirect(request.GET['next'] if 'next' in request.GET else 'User_leave_requests')

        messages.error(request, 'Nazwa użytkownika lub hasło jest niepoprawne.')

    context = {'page': page}
    return render(request, 'Users/login.html', context)


def logout_user(request):
    # Get logged in user
    logout(request)
    messages.info(request, 'Pomyślnie wylogowano!')
    return redirect('login')

@login_required(login_url='login')
def edit_account(request):

    page = 'edit_account'
    user = request.user
    profile = user.profile
    profile_form = ProfileForm(instance=profile)
    password_form = ChangePasswordForm(user)

    if request.method == 'POST':
        if 'profile_save' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                email = profile_form.cleaned_data['email'].lower()

                if profile_form.instance.user and User.objects.exclude(id=profile_form.instance.user.id).filter(
                        email=email).exists():
                    profile_form.add_error('email', "Podany adres e-mail jest już w użyciu.")
                else:
                    profile_form.instance.user.email = email
                    profile_form.save()
                    messages.success(request, 'Dane zostały zaktualizowane.')
                    return redirect('edit_account')
        elif 'password_save' in request.POST:
            password_form = ChangePasswordForm(user, request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password1 = password_form.cleaned_data.get('new_password1')
                new_password2 = password_form.cleaned_data.get('new_password2')

                if not password_form.user.check_password(old_password):
                    password_form.add_error('old_password', "Podane hasło jest niepoprawne!")
                elif new_password1 and new_password2 and old_password == new_password1:
                    password_form.add_error('new_password1', "Nowe hasło jest takie same jak stare!")
                elif new_password1 and new_password2 and new_password2 != new_password1:
                    password_form.add_error('new_password2', "Hasła nie są takie same!")
                else:
                    password_form.save(commit=True)
                    messages.success(request, 'Hasło zostało zmienione. Zaloguj się ponownie.')
                    return redirect('edit_account')

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'page': page,
    }

    return render(request, 'Users/user_profile_form.html', context)

@manager_required(login_url='login')
def add_employee(request):
    page = 'register'
    user_form = CustomUserCreationForm()
    profile_form = ProfileCreationForm()

    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        profile_form = ProfileCreationForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            email = user_form.cleaned_data['email'].lower()
            username = user_form.cleaned_data['last_name'] + user_form.cleaned_data['first_name'][0]

            counter = 1
            base_username = username.lower()
            while User.objects.filter(username=username).exists():
                username = base_username + str(counter)
                counter += 1
            
            user = user_form.save(commit=False)
            user.email = user.email.lower()
            user.username = username

            # Check if user with the same email already exists
            if User.objects.filter(email=email).exists():
                user_form.add_error('email', 'Ten adres email jest już w użyciu.')
            else:
                user.save()

                profile = user.profile
                profile.contract_type = profile_form.cleaned_data['contract_type']
                if profile.contract_type == '2':
                    profile.available_leave = 13
                profile.save()

                messages.success(request, 'Konto pracownika zostało utworzone!')
                return redirect('add_employee')
        else:
            messages.error(request, 'Wystąpił problem podczas rejestracji')

    context = {'page': page, 'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'Users/add_employee.html', context)