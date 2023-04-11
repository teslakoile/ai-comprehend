from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'mysite'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
    path('test/', views.test, name='test'),
]
