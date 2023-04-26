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
    path("admin_indexsearch", views.admin_indexsearch),
    path("admin_home", views.admin_home),
    path("findallposts", views.findallposts),
    path("admin_findallposts", views.admin_findallposts),
    path("keywordsearch", views.keywordsearch),  
  
]
