"""django_project URL Configuration
"""
from django.contrib import admin
from django.urls import path
from frontend import views

urlpatterns = [
    path('admin/', admin.site.urls),    
    path("",views.index),
    path("requrls",views.requrls),
    path("admin_api", views.admin_api), 
    #path("admin_apisimple", views.admin_apisimple), 
    path("admin_home", views.admin_home),  
    path("usersearch", views.usersearch),  
    path("userseesposts", views.userseesposts),
  
     
]
