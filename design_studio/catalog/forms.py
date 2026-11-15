import re

from django import forms
from django.core.exceptions import ValidationError
from .models import User

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
        widget=forms.TextInput(attrs={
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


