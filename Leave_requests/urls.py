from django.urls import path

from . import views

urlpatterns = [
    path('User_leave_requests/', views.User_leave_requests, name="User_leave_requests"),
]
