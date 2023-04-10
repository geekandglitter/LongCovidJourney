from django.shortcuts import render
 

# Create your views here.
def index(request):
  return render(request, "blog_ext/index.html", {})


def requrls(request): # This requests urls from the blog
  return render(request, "blog_ext/requrls.html", {})


def soup_scrape(request):
  return render(request, "soup_scrape.html", {})