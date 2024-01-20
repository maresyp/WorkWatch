from django.urls import path

from . import views

urlpatterns = [
    path('logout/', views.logout_user, name="logout"),
    path('', views.login_user, name="login"),

    path('edit_account/', views.edit_account, name="edit_account"),
]
