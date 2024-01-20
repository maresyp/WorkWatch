from django.urls import path

from . import views

urlpatterns = [
    path('user_leave_requests/', views.User_leave_requests, name="user_leave_requests"),
]
