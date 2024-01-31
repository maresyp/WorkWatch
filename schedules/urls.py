from django.urls import path

from . import views

urlpatterns = [
    path('user_schedule/', views.user_schedule, name="user_schedule"),
    path('user_schedule/<uuid:schedule>', views.user_schedule, name="user_schedule"),
    path('user_schedule_navigation/<uuid:schedule>/<str:direction>', views.user_schedule_navigation, name="user_schedule_navigation"),

    path('manager_schedules/', views.manager_schedules, name="manager_schedules"),
    path('manager_schedules/<int:user_id>', views.manager_schedules, name="manager_schedules"),
    path('manager_schedules/<int:user_id>/<uuid:schedule_id>', views.manager_schedules, name="manager_schedules"),
    path('manager_schedules/<int:user_id>/<uuid:schedule_id>/<str:direction>', views.manager_schedules, name="manager_schedules"),
    path('manager_schedules/<int:user_id>/<str:direction>/<str:date_str>', views.manager_schedules, name="manager_schedules_nav"),

    path('create_schedule/<int:user_id>/<str:date_str>/', views.create_schedule, name='create_schedule'),
    path('update_schedule/<int:user_id>/<str:date_str>/', views.update_schedule, name='update_schedule'),
]
