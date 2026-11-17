import re

from django import forms
from django.core.exceptions import ValidationError
from .models import User, Application, validate_photo_file, Category, validate_design_file
from django.contrib.auth import authenticate

class UserRegisterForm(forms.ModelForm):
    fio = forms.CharField(
        label='ФИО',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ivanov-ivan',
        })
    )

    username = forms.CharField(
        label='Логин',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ivanov-ivan'
        })
    )
    email = forms.EmailField(
        label='Email',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ivan@example.com'
        })
    )

    password = forms.CharField(
        label='Пароль',
        max_length=150,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
    )

    password_confirm = forms.CharField(
        label='Повтор пароля',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '********'
        })
    )

    agree_data_processing = forms.BooleanField(
        label='Согласие на обработку персональных данных',
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class' : 'form-check-input',
        }),
        error_messages={
            'required' : 'Необходимо согласиться на обработку персональных данных.'
        }
    )

    class Meta:
        model = User
        fields = ('fio', 'username', 'email', 'password')

    def clean_fio(self):
        fio = self.cleaned_data.get('fio', '').strip()
        if not re.fullmatch(r'^[а-яА-ЯёЁ\s-]+$', fio):
            raise ValidationError('ФИО может содержать только кириллические буквы, дефис и пробелы')
        return fio

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not re.fullmatch(r'^[a-zA-Z0-]+$', username):
            raise ValidationError('Логин может содержать только латинские буквы и дефис.')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        return email

    def clean(self):
        cleared_data = super().clean()
        password = self.cleaned_data.get('password')
        password_confirm = cleared_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'пароли не совпадают. Пожалуйста повторите ввод')
        return cleared_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserLoginForm(forms.Form):

    username = forms.CharField(
        label='Логин',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин',
        })
    )

    password = forms.CharField(
        label='Пароль',
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise ValidationError('Неверный логин или пароль. Проверьте данные')
            elif not self.user_cache.is_active:
                raise ValidationError('Этот аккаунт деактивирован')
        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)

class ApplicationCreateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ('title', 'description', 'category', 'photo')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Дизайн гостинной в стиле лофт'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Подробно опишите требования к интерьеру, бюджет, особенности помещения и т.д.'
            }),

            'category': forms.Select(attrs={
                'class': 'form-select',
            }),

            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                "accept": '.jpg, .jpeg, .png, .bmp'
            }),
        }

        labels = {
            'title': 'Название заявки',
            'description': 'Описание заявки',
            'category': 'Категория дизайна',
            'photo': 'Фото помещения или его план (jpg, jpeg, png, bmp до 2 МБ)',
        }

        def clean_photo(self):
            photo = self.cleaned_data.get('photo')
            if photo:
                validate_photo_file(photo)
            else:
                raise ValidationError('Прикрепление фото помещения или плана обязательно')
            return photo

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Скандинавский стиль или 3D-визуализация'
            })
        }

        labels={
            'name': 'Название категории'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Название категории не может быть пустым')
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError('Категория с таким названием уже существует')
        return name

class StatusToInProgressForm(forms.Form):
    comment = forms.CharField(
        label = 'Комментарий администратора',
        required = True,
        widget = forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Укажите комментарий к заявке (назначенный дизайнер, сроки, уточнения)...'
        }),
        error_messages = {
            'required': 'Для перевода в статус "Принято в работу" необходимо обязательно указать комментарий'
        }
    )

class StatusToCompletedForm(forms.Form):
    design_image = forms.ImageField(
        label='Изображение созданного дизайна',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.jpg, .jpeg, .png, .bmp'
        }),
        error_messages = {
            'required': 'Для перевода в статус "Выполнено необходимо обязательно прикрепить изображение дизайна"'
        }

    )

    def clean_design_image(self):
        image = self.cleaned_data.get('design_image')
        if image:
            validate_design_file(image)
        return image