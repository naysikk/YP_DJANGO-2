from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm


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
        return redirect('cabinet')

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
            return redirect('cabinet')
        else:
            form = UserLoginForm()

        return render(request, 'Неверный пароль')

    else:
        form = UserLoginForm()

    return render(request, 'register/login.html', {'form': form})





