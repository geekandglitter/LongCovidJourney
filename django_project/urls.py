"""django_project URL Configuration
"""
from django.contrib import admin
from django.urls import path
from frontend import views

urlpatterns = [
    path('admin/', admin.site.urls),    
    path("",views.index),
    path("requrls",views.requrls),
    path("admin_findallposts", views.admin_findallposts), 
    path("admin_scrape", views.admin_scrape),
    path("admin_home", views.admin_home),    
    path("admin_findallposts", views.admin_findallposts),
    path("usersearch", views.usersearch),  
    path("userseesposts", views.userseesposts),
  
     
]
