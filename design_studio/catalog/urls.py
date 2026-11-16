from django.contrib.auth import logout
from django.urls import path
from . import views

urlpatterns =[
    path('register/',views.register_view, name='register'),
    path('login/',views.login_view, name='login'),
    path('', views.index, name='index'),

    path('logout/', views.logout_view, name='logout'),
    path('application/create/',views.create_application_view, name='application-create'),
    path('cabinet/',views.cabinet_view, name='cabinet'),
    path('application/<int:pk>/delete/', views.delete_application_view, name='application-delete'),
]