from django.contrib import admin

# Register your models here. 
from .models import AllPosts 
from .models import SearchTerms 
from .models import AllContents 
admin.site.register(AllPosts)
admin.site.register(SearchTerms)
admin.site.register(AllContents)
 
