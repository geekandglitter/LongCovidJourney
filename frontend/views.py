from django.shortcuts import render
import requests 
import json
import datetime as d
from operator import itemgetter

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







 


###################################################
# This view GETS the posts using Google Blogger API and "request.get"
###################################################
""" This view uses the Google Blogger API to retreive all the posts. All I needed was an API key. 
"""


#@user_passes_test(check_admin)
def admin_findallposts(request):

    def request_by_year(edate, sdate):

        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in windows.

        url_part_1 = "https://www.googleapis.com/blogger/v3/blogs/639737653225043728/posts?endDate="
        url_part_2 = edate + "&fetchBodies=false&maxResults=500&startDate=" + sdate
        url_part_3 = "&status=live&view=READER&fields=items(title%2Curl)&key=AIzaSyDleLQNXOzdCSTGhu5p6CPyBm92we3balg"
        url = url_part_1 + url_part_2 + url_part_3

        r = requests.get(url, stream=True)
        q = json.loads(r.text)  # this is the better way to unstring it
        if not q:
            s = []
        else:
            s = q['items']

        return s

    accum_list = []
    c_year = int(d.datetime.now().year)

    for the_year in range(2014, c_year + 1):
        enddate = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        startdate = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"

        t = request_by_year(enddate, startdate)
        accum_list = accum_list + t

    sorteditems = sorted(accum_list, key=itemgetter('title'), reverse=True)
    counter = 0
    newstring = " "
    for mylink in sorteditems:
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring

    return render(request, 'frontend/admin_findallposts.html', {'allofit': newstring, 'count': counter})

def admin_indexsearch(request):
  return render(request, "frontend/admin_indexsearch.html", {})

def admin_home(request):
  return render(request, "frontend/admin_home.html", {})