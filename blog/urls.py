from django.urls import path,include
from . import views

urlpatterns = [
    path('accounts/',include('allauth.urls')),
    path('', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/create/', views.blog_create, name='blog_create'),
    path('blogs/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('blogs/<int:pk>/update/', views.blog_update, name='blog_update'),
    path('blogs/<int:pk>/delete/', views.blog_delete, name='blog_delete'),
    path('blogs/<int:pk>/like/', views.blog_like, name='blog_like'),
    path('blogs/<int:pk>/loading/', views.blog_loading, name='blog_loading'),
    path('blog/<int:pk>/perm/<int:us_id>/<str:action>/', views.blog_perm, name='blog_perm'),
    path('blogs/user/', views.blog_user_list, name='blog_user_list'),
    path('request-counts/',views.request_count_view,name='request_count_view'),
]
