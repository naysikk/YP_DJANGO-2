from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, ApplicationCreateForm
from .models import Application


def register_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Регистрация прошла успешно!')
            login(request, user)
            return redirect('cabinet')
        else:
            messages.error(request, 'Пожалуйста исправьте ошибки в форме регистрации.')
    else:
        form = UserRegisterForm()
    return render(request, 'register/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_panel')
        return redirect('index')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Вы успешно вошли как {user.username}!!')

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_staff or user.is_superuser:
                return redirect('admin_panel')
            return redirect('index')
        else:
            messages.error(request, 'Неверный логин или пароль')
    else:
        form = UserLoginForm()

    return render(request, 'register/login.html', {'form': form})

def index(request):
    in_progress_count = 1,
    completed_apps = 1,

    contex ={
        'in_progress_count': in_progress_count,
        'completed_apps': completed_apps,
    }
    return render(request, 'index.html', contex)

def logout_view(request):
    logout(request)
    messages.info(request,'Вы успешно вышли из системы')
    return redirect('index')

@login_required
def create_application_view(request):
    if request.method == 'POST':
        form = ApplicationCreateForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = Application.STATUS_NEW
            application.save()
            messages.success(request, f'Заявка "{application.title}" успешно создана и получила статус "Новая"!!')
            return redirect('index')
        else:
            messages.error(request, 'Пожалуйста, проверьте корректность заполнения полей заявки')
    else:
        form = ApplicationCreateForm()

    return render(request, 'catalog/application_form.html', {'form': form})




