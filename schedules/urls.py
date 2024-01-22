from django.urls import path

from . import views

urlpatterns = [
    path('user_schedule/', views.user_schedule, name="user_schedule"),
    path('manager_schedules/', views.manager_schedules, name="manager_schedules"),
]
