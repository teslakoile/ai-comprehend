"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib import messages


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


urlpatterns = [
    path('register/', views.register, name='register'),
    path('success/', views.success, name='success'),
    path('login/', views.login_view, name='login'),
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('test/', views.test, name='test'),
    path('update_user_answer/', views.update_user_answer, name='update_user_answer'),
    path('user_history/<str:username>/', views.get_user_history, name='user_history'),
    path('all_users_history/', views.get_all_users_history, name='all_users_history'),
    path('next_question/', views.next_question, name='next_question'),

]

