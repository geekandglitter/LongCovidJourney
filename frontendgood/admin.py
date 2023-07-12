from django.contrib import admin

# Register your models here. 
from .models import AllPosts 
from .models import SearchTerms 
  
admin.site.register(AllPosts)
admin.site.register(SearchTerms)
 
 
