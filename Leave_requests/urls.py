from django.urls import path

from . import views

urlpatterns = [
    path('User_leave_requests/', views.User_leave_requests, name="User_leave_requests"),
    path('Manager_leave_requests/', views.Manager_leave_requests, name="Manager_leave_requests"),
    path('Manager_leave_requests/<int:user_id>/', views.Manager_leave_requests, name="Manager_leave_requests"),
    path('accept-leave-request/<uuid:request_id>/', views.accept_leave_request, name='accept_leave_request'),
    path('decline-leave-request/<uuid:request_id>/', views.decline_leave_request, name='decline_leave_request'),
    path('search-users/', views.search_users, name='search-users'),
]
