import os

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings


class User(AbstractUser):
    fio = models.CharField(
        max_length=150,
        verbose_name='ФИО',
        help_text='ФИО (только кириллические буквы, дефис и пробелы)'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username} ({self.fio if self.fio else self.get_full_name()})'

def validate_photo_file(file):
    max_size_mb = 2
    if file.size > max_size_mb * 1024 * 1024:
        raise  ValidationError(f'Максимальный размер файла не должен превышать {max_size_mb} MB')
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.bmp']:
        raise ValidationError(f'Недопустимый формат файла({ext}). Разрешены: .jpg, .jpeg, .png, .bmp')

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории'
    )

    class Meta:
        verbose_name = 'Катергория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

def validate_design_file(file):
    max_size_mb = 5
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f'Максимальный размер файла не должен превышать {max_size_mb} MБ')

    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    if ext not in valid_extensions:
        raise ValidationError(
            f'Недоступный формат файла({ext}). Разрешён только: .jpg, .jpeg, .png, .bmp'
        )

class Application(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in-progress'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'Принято в работу'),
        (STATUS_COMPLETED, 'Выполнено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name= 'Пользователь',
    )

    title = models.CharField(
        max_length=100,
        verbose_name='Название заявки'
    )

    description = models.TextField(
        verbose_name='Описание заявки',
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='Категория'
    )

    photo = models.ImageField(
        upload_to='photos/',
        validators=[validate_photo_file],
        verbose_name='Фото помещения или его план',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Временная метка добавления'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        verbose_name='Статус',
    )

    comment = models.TextField(
        blank=True,
        null=True,
        verbose_name='Комментарий администратора'
    )

    design_image = models.ImageField(
        upload_to='design/',
        blank=True,
        null=True,
        verbose_name='Изображение дизайна'
    )

    class Meta:
        verbose_name='Заявка',
        verbose_name_plural='Заявки',
        ordering=['-created_at']

    @property
    def is_deletable(self):
        return self.status == self.STATUS_NEW,

    @property
    def can_change_status(self):
        return self.status == self.STATUS_NEW,