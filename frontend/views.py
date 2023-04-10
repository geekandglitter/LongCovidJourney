from django.shortcuts import render
 

# Create your views here.
def index(request):
  return render(request, "frontend/index.html", {})


def requrls(request): # This requests urls from the blog
  return render(request, "frontend/requrls.html", {})


def soup_scrape(request):
  return render(request, "soup_scrape.html", {})
  
# this view makes sure the user is a superuser first before they can perform admin functions
def check_admin(user):
   return user.is_superuser
  
# this is the view that goes into the blog, gets all the blog titles and their urls, and puts them in a model
#@user_passes_test(check_admin)
def admin_findallposts(request):
  # put code here
  return render(request, "frontend/admin_findallposts.html", {})

def admin_indexsearch(request):
  return render(request, "frontend/admin_indexsearch.html", {})

def admin_home(request):
  return render(request, "frontend/admin_home.html", {})