from django.shortcuts import render
import requests 
import json
import datetime as d
from .models import AllPosts
#from operator import itemgetter
from django.contrib.auth.decorators import user_passes_test 
from frontend.utils import search_func # this function does the model query heavy lifting for modelsearch_view 
from .forms import UserForm 
 



 
def index(request):
  return render(request, "frontend/index.html", {})
def is_superuser(user):
  return user.is_superuser
def requrls(request): # This requests urls from the blog
  return render(request, "frontend/requrls.html", {})

 
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
                             
            form.data['user_search_terms'] = (', '.join(user_string_parts) )   


             
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
 
  all_posts = AllPosts.objects.all().reverse()
  all_posts = AllPosts.objects.all()   
  accum=""
  counter=0
  for one_post in all_posts:
    counter+=1 
    accum=accum +(str(one_post))  
   
  return render(request, "frontend/userseesposts.html", {'allofit': accum, 'count': counter})   
 
################################################
# This view GETS the posts using Google Blogger API and "request.get" for the admin and puts the results in a model  
# ################################################
 
@user_passes_test(lambda user: user.is_superuser, login_url='/')
def admin_api(request):        
 
    accum_list = []  # this will become a list of dictionaries
    c_year = int(d.datetime.now().year)
    
    for the_year in range(2017, c_year +1 ):
        from django.conf import settings 
        base_url = (
         "https://www.googleapis.com/"
         "blogger/v3/blogs/" + settings.THE_BLOG_ID + "posts/?"
        )
         
        end_date = str(the_year) + "-12-31T00%3A00%3A00-00%3A00"
        start_date = str(the_year) + "-01-01T00%3A00%3A00-00%3A00"
        fields = "items(content%2Ctitle%2Curl)"
        api_key = "AIzaSyBq-EPVMpROwsvmUWeo-AYAchzLuTpXLDk"
        max_results = "500"

        parameters = {
           "startDate": start_date,
           "endDate": end_date,
           "fields": fields,
           "key": api_key,
           "maxResults": max_results
          }

        url = base_url + "&".join([f"{key}={value}" \
                                   for key, value in parameters.items()])    
        r = requests.get(url, stream=True)      
        q = json.loads(r.text)            
        if not q:
            s = []
        else:            
            s=q['items']      
        accum_list = accum_list + s      
    sorteditems = accum_list
    #sorteditems.reverse()
   
    
    counter = 0
    newstring = " "
    # Now we get ready to update the database
    AllPosts.objects.all().delete()  # clear the table 
    for mylink in sorteditems:         
        counter += 1
        newstring = "<a href=" + mylink['url'] + ">" + \
            mylink['title'] + "</a>" + "<br>" + newstring
       
        newrec = AllPosts.objects.create(
            title=mylink['title'],
            hyperlink="<a href=" + mylink['url'] + ">" + \
               mylink['title'] + "</a>" + "<br>",
            url=mylink['url'],
            fullpost=mylink['content']
        )         
        newrec.save() 
    return render(request, 'frontend/admin_api.html', \
                  {'allofit': newstring, 'count': counter}) 
   
###################################################
 