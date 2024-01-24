from django.urls import path

from . import views

urlpatterns = [
    path('user_schedule/', views.user_schedule, name="user_schedule"),
    path('user_schedule/<uuid:schedule>', views.user_schedule, name="user_schedule"),
    path('user_schedule_navigation/<uuid:schedule>/<str:direction>', views.user_schedule_navigation, name="user_schedule_navigation"),

    path('manager_schedules/', views.manager_schedules, name="manager_schedules"),
]
