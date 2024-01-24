from django.urls import path

from . import views

urlpatterns = [
    path('user_schedule/', views.user_schedule, name="user_schedule"),
    path('user_schedule/<uuid:schedule>', views.user_schedule, name="user_schedule"),

    path('user_previous_schedule/<uuid:schedule>', views.user_previous_schedule, name="user_previous_schedule"),
    path('user_next_schedule/<uuid:schedule>', views.user_next_schedule, name="user_next_schedule"),

    path('manager_schedules/', views.manager_schedules, name="manager_schedules"),
]
