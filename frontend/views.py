from django.shortcuts import render
import requests 
import json
import datetime as d
from .models import AllPosts
from operator import itemgetter
from bs4 import BeautifulSoup
from .models import AllContents
from django.contrib.auth.decorators import user_passes_test 
from frontend.utils import search_func # this function does the model query heavy lifting for modelsearch_view 
from .forms import UserForm 
from django.db import IntegrityError
import sys



 
def index(request):
  return render(request, "frontend/index.html", {})
def is_superuser(user):
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

        url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts/?"  + "startDate=" + sdate + "&fields=items(content%2Ctitle%2Curl)&key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk&maxResults=500"     

        r = requests.get(url, stream=True)
        q = json.loads(r.text)            
        if not q:
            s = []
        else:            
            s=q['items']             
        return (s)

    accum_list = []  # this will become a list of dictionaries
    c_year = int(d.datetime.now().year)

    for the_year in range(2022, c_year ):
        enddate = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        startdate = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"
        t = request_by_year(enddate, startdate)
        accum_list = accum_list + t     
    
    sorteditems = sorted(accum_list, key=itemgetter('title'))  
    sorteditems.reverse()
    
    counter = 0
    newstring = " "
    # Now we get ready to update the database
    AllPosts.objects.all().delete()  # clear the table
    AllContents.objects.all().delete()  # clear the table
    for mylink in sorteditems:
         
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring
            # Below, notice I stuff the title in with the body. It makes the title search part of the contents search.
        newrec = AllPosts.objects.create(
            anchortext=mylink['title'],
            hyperlink="<a href=" + mylink['url'] + ">" + mylink['title'] + "</a>" + "<br>",
            url=mylink['url'],
            fullpost=mylink['content']
        )
         
        newrec.save()

        newrec = AllContents.objects.create(
            title=mylink['title'],
            hyperlink=mylink['url'],
            fullpost=mylink['content']
        )
        newrec.save()  
          

    return render(request, 'frontend/admin_findallposts.html', {'allofit': newstring, 'count': counter})

 

#############
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_scrape(request):
    '''
    Scrape the contents of every recipe post
    Here's the psuedocode:
    1.Get the url and anchortext from AllPosts
    2.Delete AllContents
    3.Loop through the hyperlinks, get post, finall inside post-body,       store contents, url and anchortext in AllContents            
    4. Put something out to the template  
    '''
    # First, get all the urls from AllPosts
    instance = AllPosts.objects.filter().values_list('url', 'anchortext')
    
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
             
    return render(request, "frontend/admin_scrape.html", {})  

############# 
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_home(request):
  return render(request, "frontend/admin_home.html", {})

############# 
def usersearch(request):
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
                user_terms = [each_string.lower() for each_string in user_terms] 
                # I like them to all be lowercase               
                context = search_func(user_terms)  
                # The search_func does all the query heavy lifting 
                context.update({'form': form})             
            else:    
                context = {'form': form}       
            return render(request, 'frontend/usersearch.html', context)    
        except IndexError:
            context = {'form': form}         
    else: # This code executes the first time this view is run. It shows an empty form to the user  
        context = {'form': form}     
    return render(request, 'frontend/usersearch.html', context) 


############# 
def userseesposts(request):
  """
  retrieve the contents of the AllPosts model
  """
  
  all_posts = AllPosts.objects.all()
  
  accum=""
  counter=0
  for one_post in all_posts:
    counter+=1 
    accum=accum +(str(one_post))
   
 
  return render(request, "frontend/userseesposts.html", {'allofit': accum, 'count': counter})  


############# 
############# 
############# 
############# 
# I might be able to use this for title and url as well. Just don't change the original finallposts
############# 
   
 