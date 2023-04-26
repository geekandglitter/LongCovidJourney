from django.shortcuts import render
import requests 
import json
import datetime as d
from .models import AllPosts
from operator import itemgetter
from bs4 import BeautifulSoup
from .models import AllContents
from django.contrib.auth.decorators import user_passes_test 
from frontend.utils import search_func 
# this function does the model query heavy lifting for modelsearch_view 
 
from .forms import UserForm

 

 
def index(request):
  return render(request, "frontend/index.html", {})
def is_superuser(user):
    print ("User is", user)
    print("Truthiness is", user.is_superuser)
    return user.is_superuser
  
  


def requrls(request): # This requests urls from the blog
  return render(request, "frontend/requrls.html", {})

 


def soup_scrape(request):
  return render(request, "frontend/soup_scrape.html", {})
  
 

###################################################
# This view GETS the posts using Google Blogger API and "request.get" for the admin and puts the results in a model  
###################################################
""" This view uses the Google Blogger API to retreive all the posts. All I needed was an API key.  Uses the blogger API and the requests module to get all the posts, and stores one recipe per record in the database
"""
 
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_findallposts(request):
 
    
    def request_by_year(edate, sdate):
        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in windows.

        url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts?endDate=" + edate + "&fetchBodies=false&maxResults=500&startDate=" + \
            sdate + \
            "&status=live&view=READER&fields=items(title%2Curl)&key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk"

        r = requests.get(url, stream=True)
        q = json.loads(r.text)  # this is the better way to unstring it
        if not q:
            s = []
        else:
            s = q['items']
        return (s)

    accum_list = []  # this will become a list of dictionaries
    c_year = int(d.datetime.now().year)

    for the_year in range(2014, c_year + 1):
        enddate = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        startdate = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"
        t = request_by_year(enddate, startdate)
        accum_list = accum_list + t

    #sorteditems = sorted(accum_list, key=itemgetter('title'), reverse=True)
    sorteditems = sorted(accum_list, key=itemgetter('title'))
    sorteditems.reverse()
    counter = 0
    newstring = " "
    # Now we get ready to update the database
    AllPosts.objects.all().delete()  # clear the table
    for mylink in sorteditems:
         
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring
            # Below, notice I stuff the title in with the body. It makes the title search part of the contents search.
        newrec = AllPosts.objects.create(
            anchortext=mylink['title'],
            hyperlink="<a href=" + mylink['url'] + ">" + mylink['title'] + "</a>" + "<br>",
            url=mylink['url']
        )
        newrec.save()

    return render(request, 'frontend/admin_findallposts.html', {'allofit': newstring, 'count': counter})

     



###################################################
# This view GETS the posts for the end user using Google Blogger API and # "request.get" and shows the results
###################################################
""" This view uses the Google Blogger API to retreive all the posts. All I needed was an API key. 
"""

 
def findallposts(request):

    def request_by_year(edate, sdate):

        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in windows.

        url_part_1 = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts?endDate="
        url_part_2 = edate + "&fetchBodies=false&maxResults=500&startDate=" + sdate
        url_part_3 = "&status=live&view=READER&fields=items(title%2Curl)&key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk"
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

 





#############
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')

def admin_indexsearch(request):
    '''
    Scrape the contents of every recipe post
    Here's the psuedocode:
    1. Go into the AllPosts model
    2.Retrieve all the hyperlinks and put them in a list
    3. Loop through the hyperlinks
        a. Get post and find everything inside post-body, eliminate all html
        b. Store all contents in the new model AllContents.Fullpost    
        c. Also update AllCOntents.Hyperlink        
    4. Put something out to the template 
 
    '''
    # First, get all the urls from AllPosts
    instance = AllPosts.objects.filter().values_list('url', 'anchortext')
    from django.db import IntegrityError
    # For now, I'm starting over each time, by emptying out AllContents
    AllContents.objects.all().delete()  # clear the table 
    for hyper, title in instance: 
         
        getpost = requests.get(hyper)
        soup = BeautifulSoup(getpost.text, 'html.parser')            
        soup_contents = soup.find("div", class_="post-body entry-content") 
        stripped = title + soup_contents.get_text()
        stripped=stripped.replace('\n',' ') # need to replace newline with a blank
        stripped = ' '.join(stripped.split()) # remove all multiple blanks, leave single blanks      
        try: 
            newrec = AllContents.objects.create(
                fullpost=stripped,       
                hyperlink=hyper,
                title=title
            )
        except IntegrityError:
            return render(request, 'frontend/error')    
        newrec.save()
      

             
    return render(request, "frontend/admin_indexsearch.html", {})

 
  
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_home(request):
  print("HI I'm in admin_home")
  return render(request, "frontend/admin_home.html", {})



############# 
def keywordsearch(request):
    '''      
    Below I query using values_list(). The alternative would have been values() which creates a nice dictionary,
    which should be easier because I can see the keywords, but whatever. So instead I am referring to the indices:
    [0] # search terms
    [1] # url
    [2] # title    
    [-1] # the number of search terms found per recipe
    ''' 
    
    form = UserForm(request.POST)       
    if request.method == 'POST': # this means the user has filled out the form     
        try:           
            user_terms=""   
            form.data = form.data.copy()  # Make a mutable copy
            if form.data['user_search_terms'][-1] == ",": # Ditch any trailing commas          
           
                form.data['user_search_terms'] = form.data['user_search_terms'][:-1]
                i = 1
                while True:
                    if form.data['user_search_terms'][-1] == ",":
                        form.data['user_search_terms'] = form.data['user_search_terms'][:-1]
                    else:
                        break    
                 
            # Now I also have to handle any duplicate commas           
            user_string_parts = form.data['user_search_terms'].split(',') 
            user_string_parts = [part.strip() for part in user_string_parts ]
            #while("" in user_string_parts) :  # THis while loop doesn't look necessary
            #    user_string_parts.remove("")                
            form.data['user_search_terms'] = (', '.join(user_string_parts) )   


            # Next, run it thorugh modelform validation, then call my search_func to do all the query heavy lifting
            if form.is_valid():    
                cd = form.cleaned_data  # Clean the user input
                user_terms = cd['user_search_terms']  # See forms.py
                user_terms = [each_string.lower() for each_string in user_terms] # I like them to all be lowercase               
                context = search_func(user_terms) 
              
              # The function does all the query heavy lifting                               
                context.update({'form': form}) 
            
            else:    
                context = {'form': form}       
            return render(request, 'frontend/keywordsearch.html', context)    
        except IndexError:
            context = {'form': form}         
    else: # This code executes the first time this view is run. It shows an empty form to the user  
        context = {'form': form}     
    return render(request, 'frontend/keywordsearch.html', context) 



 