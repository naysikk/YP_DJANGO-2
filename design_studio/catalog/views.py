from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm, ApplicationCreateForm, CategoryForm, StatusToInProgressForm, StatusToCompletedForm
from .models import Application, Category


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

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
            return redirect('admin-panel')
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
                return redirect('admin-panel')
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


@user_passes_test(is_admin, login_url='login')
def admin_panel_view(request):
    status_filter = request.GET.get('status', 'all')
    all_apps = Application.objects.select_related('user', 'category').all()

    total_count = all_apps.count()
    new_count = all_apps.filter(status=Application.STATUS_NEW).count()
    in_progress_count = all_apps.filter(status=Application.STATUS_IN_PROGRESS).count()
    completed_count = all_apps.filter(status=Application.STATUS_COMPLETED).count()

    if status_filter in [Application.STATUS_IN_PROGRESS, Application.STATUS_COMPLETED]:
        application = all_apps.filter(status=status_filter).order_by('-created_at')
    else:
        application = all_apps.order_by('-created_at')

    categories = Category.objects.all().order_by("-id")
    category_form = CategoryForm()

    context = {
        'applications': application,
        'categories': categories,
        'category_form': category_form,
        'status_filter': status_filter,
        'total_count': total_count,
        'new_count': new_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
    }
    return render(request, 'catalog/admin_panel.html', context)

@user_passes_test(is_admin, login_url='login')
def admin_change_status_in_progress(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.status != Application.STATUS_NEW:
        messages.error(request, 'Смена статуса с "Принято в работу" или "Выполнено" невозможна')
        return redirect('admin-panel')

    if request.method == 'POST':
        form = StatusToInProgressForm(request.POST)
        if form.is_valid():
            application.status = Application.STATUS_IN_PROGRESS
            application.comment = form.cleaned_data['comment']
            application.save()
            messages.success(request, f'Заявка #{application.pk} переведена в статус "Принято в работу"')
        else:
            messages.error(request, 'Для перевода заявки в работу обязательно укажите комментарий')
    return redirect('admin-panel')

@user_passes_test(is_admin, login_url='login')
def admin_change_status_completed(request, pk):
    application = get_object_or_404(Application, pk=pk)

    if application.status != Application.STATUS_NEW:
        messages.error(request, 'Смена статуса с "Принято в работу" или "Выполнено" невозможна')
        return redirect('admin-panel')

    if request.method == 'POST':
        form = StatusToCompletedForm(request.POST, request.FILES)
        if form.is_valid():
            application.status = Application.STATUS_COMPLETED
            application.design_image = form.cleaned_data['design_image']
            application.save()
            messages.success(request, f'Заявка #{application.pk} успешно выполнена и прикреплён дизайн!')
        else:
            messages.error(request, 'Для завершения заявки обязательно загрузите изображение дизайна')
    return redirect('admin-panel')

@user_passes_test(is_admin, login_url='login')
def admin_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Категория "{category.name}" успешно добавлена')
        else:
            for field, errs in form.errors.items():
                for e in errs:
                    messages.error(request, f'Ошибка категории: {e}')
    return redirect('admin-panel')

@user_passes_test(is_admin, login_url='login')
def admin_delete_category(request, pk):
    category =get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = category.name
        apps_count = category.applications.count()
        category.delete()
        messages.success(
            request,
            f'Категория "{name}" и все привязанные заявки ({apps_count} шт.) были безвозвратно удалены'
        )
        return redirect('admin-panel')

    return render(request,'catalog/category_confirm_delete.html', {'category': category})













