from django.contrib import admin
from django.urls import path,include,re_path
from django.shortcuts import redirect

def catch_all(request):
    return redirect('blog/')  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include('blog.urls')),
    path('accounts/', include('allauth.urls')),
    # re_path(r'^.*$', catch_all),  
]