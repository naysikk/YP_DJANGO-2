from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
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
    in_progress_count = Application.objects.filter(status=Application.STATUS_IN_PROGRESS).count(),
    completed_apps = Application.objects.filter(status=Application.STATUS_COMPLETED).select_related('category').order_by('-created_at')[:4]

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

@login_required
def cabinet_view(request):
    user_apps = Application.objects.filter(user=request.user).select_related('category')

    total_count = user_apps.count()
    new_count = user_apps.filter(status=Application.STATUS_NEW).count()
    in_progress_count = user_apps.filter(status=Application.STATUS_IN_PROGRESS).count()
    completed_count = user_apps.filter(status=Application.STATUS_COMPLETED).count()

    current_filter = request.GET.get('status', 'all')
    if current_filter in [Application.STATUS_NEW, Application.STATUS_IN_PROGRESS, Application.STATUS_COMPLETED]:
        user_apps = user_apps.filter(status=current_filter)

    user_apps = user_apps.order_by('-created_at')

    context = {
        'applications': user_apps,
        'current_filter': current_filter,
        'total_count': total_count,
        'new_count': new_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
    }

    return render(request, 'catalog/cabinet.html', context)

@login_required
def delete_application_view(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)

    if not application.is_deletable:
        messages.error(
            request,
            "Заявку нельзя изменить или удалить, так как её статус уже изменён администратором на 'Принято в работу' или 'Выполнено' "
        )
        return redirect('cabinet')

    if request.method == 'POST':
        title = application.title
        application.delete()
        messages.success(request, f'Заявка "{title}" была успешно удалена')
        return redirect('cabinet')

    return render(request, 'catalog/application_confirm_delete.html', {'application': application})







