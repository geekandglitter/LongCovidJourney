from django.shortcuts import render
import requests 
import json
import datetime as d
from .models import AllPosts
from .models import NEWAllPosts
from operator import itemgetter
from bs4 import BeautifulSoup
from .models import AllContents
from .models import NEWAllContents
from django.contrib.auth.decorators import user_passes_test 
from frontend.utils import search_func # this function does the model query heavy lifting for modelsearch_view 
from .forms import UserForm 
from .forms import NEWUserForm
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
 

 

 

#############
# This is the view that scrapes with beautifulsoup 
#@user_passes_test(lambda user: user.is_superuser, login_url='/')
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

############# 
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_home(request):
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
    
    form = NEWUserForm(request.POST)       
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
            #return render(request, 'frontend/NEWkeywordsearch.html', context)
            return render(request, 'frontend/keywordsearch.html', context)   
        except IndexError:
            context = {'form': form}         
    else: # This code executes the first time this view is run. It shows an empty form to the user  
        context = {'form': form}   
        #print("context is", context)
        #sys.exit()
    #return render(request, 'frontend/NEWkeywordsearch.html', context) 
    return render(request, 'frontend/keywordsearch.html', context) 


############# 
def userseesposts(request):
  """
  retrieve the contents of the AllPosts model
  """
  
  all_posts = NEWAllPosts.objects.all()
  #print(all_posts)
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
# I might be able to use this for title and url as well. Just don't change the original findallposts
############# 
   
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_findallposts3(request):  
    url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts/?key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk&maxResults=500"
     
    accum_list = [] 
    response = requests.get(url, stream=True)
    data = json.loads(response.text)
    posts = data['items']     
    counter = 0
    newstring = " "
    NEWAllContents.objects.all().delete()  # clear the table 
    NEWAllPosts.objects.all().delete()  # clear the table
    AllContents.objects.all().delete()  # clear the table 
    AllPosts.objects.all().delete()  # clear the table
    
    
    for post in posts:
        title = post['title']
        content = post['content']
        url = post['url']
         
        #print('Title:', title)
        #print('Content:', content)
        #print('---')
        #accum_list=accum_list+[title,content, url]
        accum_list=accum_list+[content]  
         
        counter += 1
        newstring = "<a href=" + post['url'] + ">" + \
            post['title'] + "</a>" + "<br>" + newstring
            # Below, notice I stuff the title in with the body. It makes the title search part of the contents search.
        newrec = AllPosts.objects.create(
            anchortext=post['title'],
            hyperlink="<a href=" + post['url'] + ">" + post['title'] + "</a>" + "<br>",
            url=post['url']
        )
        newrec.save()
        newrec = NEWAllPosts.objects.create(
            anchortext=post['title'],
            hyperlink="<a href=" + post['url'] + ">" + post['title'] + "</a>" + "<br>",
            url=post['url']
        )
        newrec.save()
        newrec = AllContents.objects.create(
                fullpost=content,       
                hyperlink=url,
                title=title
            )
        newrec.save()
        newrec = NEWAllContents.objects.create(
                fullpost=content,       
                hyperlink=url,
                title=title
            )
        newrec.save()
               
    #sys.exit()
    
    #return render(request, 'frontend/admin_findallposts.html', {'allofit': accum_list, 'count': 0})
    return render(request, 'frontend/admin_findallposts.html', {'allofit': newstring, 'count': counter})



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
            "&status=live&view=READER&fields=items(title%2Curl%2Cid)&key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk"

     
        

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
    #print("accum_list is", accum_list)
    # This is goodness. I now have the post id, and I can use it to get the post content.
  
    sorteditems = sorted(accum_list, key=itemgetter('title'))
    sorteditems.reverse()
    counter = 0
    newstring = " "
    # Now we get ready to update the database
    AllPosts.objects.all().delete()  # clear the table
    NEWAllContents.objects.all().delete()  # clear the table 
    NEWAllPosts.objects.all().delete()  # clear the table
    AllContents.objects.all().delete()  # clear the table 
    AllPosts.objects.all().delete()  # clear the table
    the_post_ids = AllPosts.objects.values_list(
        'postid', flat=True).distinct()
    i=0
    for mylink in sorteditems:
        #print("post id is", mylink['id'])
        # Yay I have the post id for each post
        #print(" ")
        i+=1
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring
            # Below, notice I stuff the title in with the body. It makes the title search part of the contents search.
        newrec = AllPosts.objects.create(
            anchortext=mylink['title'],
            postid=mylink['id'],
            hyperlink="<a href=" + mylink['url'] + ">" + mylink['title'] + "</a>" + "<br>",
            url=mylink['url']
        )
        newrec.save()

        print("I is", i)
        print(" ")
        the_post_id= the_post_ids[i]
        url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts/" + the_post_id + "/?key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk&maxResults=500"
        response = requests.get(url, stream=True)
        data = json.loads(response.text)       
        stuff = data['content']       
        print("Stuff is", stuff)
        print(" ")
        
        newrec = AllContents.objects.create(
             hyperlink=mylink['url'],
             title=mylink['title'],  
             fullpost=stuff
        
        )
        newrec.save()





        # Now, we want to get the post contents using google blogger api
        #GET https://www.googleapis.com/blogger/v3/blogs/blogId/posts/postId
         
        url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts/" + mylink['id'] + "/?key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk&maxResults=500"
       
        # response = requests.get(url, stream=True)
        # data = json.loads(response.text)       
        # stuff = data['content']       
        # try: 
        #     newrec = AllContents.objects.create(
        #         hyperlink=mylink['url'],
        #         title=mylink['title']
        #     )
        # except IntegrityError:
        #     return render(request, 'frontend/error')    
        # newrec.save() 
      

    return render(request, 'frontend/admin_findallposts.html', {'allofit': newstring, 'count': counter})

 

#############

###################################################
###################################################
# This view GETS the posts using Google Blogger API and "request.get" for the admin and puts the results in a model   55555555555555
###################################################
""" This view uses the Google Blogger API to retreive all the posts. All I needed was an API key.  Uses the blogger API and the requests module to get all the posts, and stores one recipe per record in the database
""" 
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_findallposts5(request): 
    
    def request_by_year(edate, sdate):
        # Initially I did the entire request at once, but I had to chunk it into years because it was timing out in windows.

        url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts?endDate=" + edate + "&fetchBodies=false&maxResults=500&startDate=" + \
            sdate + \
            "&status=live&view=READER&fields=items(content%2Ctitle%2Curl)&key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk"

 

        r = requests.get(url, stream=True)
        q = json.loads(r.content)  # this is the better way to unstring it
       
        if not q:
            s = []
        else:
            s = q['items']
        #print("s: ", s)
        #print(" ")  
      
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
    NEWAllContents.objects.all().delete()  # clear the table 
    NEWAllPosts.objects.all().delete()  # clear the table
    AllContents.objects.all().delete()  # clear the table 
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
        
        newrec = AllContents.objects.create(
                     
                hyperlink=mylink['url'],
                title=mylink['title']
            )
        newrec.save()





  
   




  
     
             
    return render(request, 'frontend/admin_findallposts.html', {'allofit': newstring, 'count': counter})






############# 555555555555
# This is the view that scrapes with beautifulsoup 
#@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_indexsearch5(request):
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
    
    
    AllContents.objects.all().delete()  # clear the table 
    for url, title in instance: 
         
        getpost = requests.get(url)        
        inside = getpost.content
        #print(inside)
     
         # 
         
         
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

############# 
# 
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_newview(request):
     
     
    the_post_ids = AllPosts.objects.values_list(
        'postid', flat=True).distinct()
    #don't know if above should be flat=True
   
    # ya we now have all the post ids in a queryset 
    for i in range(the_post_ids.count()):
        print("In the loop")
       
        the_post_id= the_post_ids[i]
        #print("the_post_id is", the_post_id)
        #print(" ")
        #print("the post id is", the_post_id)
        url = "https://www.googleapis.com/blogger/v3/blogs/4571701310225125829/posts/" + the_post_id + "/?key=AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk&maxResults=500"
           
        response = requests.get(url, stream=True)
        data = json.loads(response.text)       
        stuff = data['content']       
        print("Stuff is", stuff)
        print(" ")
        newrec = AllContents.objects.create(
             fullpost=stuff          
             )            
        newrec.save()   
      
           
    
    return render(request, "frontend/admin_indexsearch.html", {}) 