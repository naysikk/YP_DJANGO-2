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

    path('admin-panel/', views.admin_panel_view, name='admin-panel'),
    path('admin-panel/application/<int:pk>/in-progress/', views.admin_change_status_in_progress, name='admin-status-in-progress'),
    path('admin-panel/application/<int:pk>/completed/', views.admin_change_status_completed, name='admin-status-completed'),

    path('admin-panel/category/add/', views.admin_add_category, name='admin-add-category'),
    path('admin-panel/category/<int:pk>/delete/', views.admin_delete_category, name='admin-delete-category'),
]