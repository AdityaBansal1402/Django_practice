from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes
from .models import Blog, User
from django.core.mail import send_mail
from django.core.cache import cache
from new.middleware.logging import url_request_count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth import logout
from blog.tasks import mail_send

def request_count_view(request):
    return JsonResponse(url_request_count)


def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        username = request.POST.get('username')

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {"error": "Email already exists."})

        password_hash = make_password(password)
        user = User.objects.create(email=email, username=username, password=password_hash)
        cache.delete('blog_user_list_cache')

        return redirect('/blog/login')

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST' and request.POST.get('email') and request.POST.get('password'):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        print('ljvbvbip')
        try:
            user = User.objects.get(email=email)
            if check_password(password, user.password):
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                # return redirect('two_factor:setup')
            
                response = redirect('/blog/blogs', {
                    'message': "Login successful!"
                })
                response.set_cookie('access_token', access_token, httponly=True, max_age=60*60) 
                cache.set('access_token',access_token,timeout=60*5)
                cache.set('user',user)
                return response
            else:
                return render(request, 'login.html', {"error": "Invalid credentials."})
        except User.DoesNotExist:
            return render(request, 'login.html', {"error": "User does not exist."})

    elif request.user.is_authenticated:
        try:
            # social_account = SocialAccount.objects.filter(user=request.user).first()
            print('request.user')
            user_account=SocialAccount.objects.get(user=request.user)
            user_id=user_account.user
            print('user_id')
            # provider = social_account.provider
            # social_token = SocialToken.objects.get(account=social_account)

            # oauth_access_token = social_token.token



            response = redirect('/blog/blogs')
            response.set_cookie('is_authenticated', request.user.is_authenticated, httponly=True, max_age=60*60)

            cache.set('user',user_id)
            cache.set('is_authenticated', request.user.is_authenticated, timeout=60*5)

            return response

        except SocialToken.DoesNotExist:
            return render(request, 'login.html', {"error": "OAuth login failed. No token found."})

    
    # print("this is my deathbed")
    return render(request, 'login.html')


@api_view(['GET'])
def blog_list(request): 
    try:
        blogs = cache.get('blog_list')

        if not blogs:
            blogs = Blog.objects.all()
            cache.set('blog_list', blogs, timeout=60*5)

        paginator = Paginator(blogs, 10)  
        page_number = request.GET.get('page') 
        page_obj = paginator.get_page(page_number)

        return render(request, 'blog/blog_list.html', {'page_obj': page_obj})

    except AuthenticationFailed:
        return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})
def blog_user_list():
    """
    Fetches the list of all users and blogs related to the logged-in user.
    """
    try:
       
        user = cache.get('user')

        users = User.objects.all()

        user_blogs = Blog.objects.filter(user_id=user.id)

        result = {
            'all_users': users,
            'user_blogs': user_blogs,
            'user': user
        }

        cache.set('blog_user_list_cache', result, timeout=300)

        return result

    except AuthenticationFailed:
        return None


@api_view(['GET', 'POST'])
def blog_create(request):
        try:
            user=cache.get('user')
            if request.method == 'POST':
                title = request.POST.get('title')
                content = request.POST.get('content')

                if not title or not content:
                    return render(request, 'blog/blog_create.html', {"error": "Title and content are required."})

                Blog.objects.create(title=title, content=content, user=user)
                cache.delete('blog_list')
                return redirect('blog_list')

            return render(request, 'blog/blog_create.html')

        except AuthenticationFailed:
            return render(request, 'login.html', {"error": "Authentication failed. Please log in again."})
        


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def blog_detail(request, pk):
        try:
            context=cache.get('blog_user_list_cache')
            if not context:
                context = blog_user_list()
            if not context:
                return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})
            
            user = context['user']
            blog = get_object_or_404(Blog, pk=pk)

            if not(blog.users_who_viewed.filter(id=user.id).exists()):
                blog.views += 1
                cache.delete('blog_list')
                blog.users_who_viewed.add(user)
                blog.save()
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'blog_{pk}',
                    {
                        'type': 'blog_update',
                        'title': blog.title,
                        'content': blog.content,
                        'likes': blog.likes
                    }
                )

                if blog.views % 1 == 0:
                    mail_send.delay(blog.title,blog.views,blog.user.email)

            context['blog'] = blog
            # print(blog.users_who_liked.all)
            return render(request, 'blog/blog_detail.html', context)

        except AuthenticationFailed:
            return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})


@api_view(['GET','POST'])
def blog_update(request, pk):
    
        try:
            user=cache.get('user')

            blog = get_object_or_404(Blog, pk=pk)

            if blog.user != user and not blog.users_access.filter(id=user.id).exists():
                return render(request, 'blog/blog_detail.html', {"error": "You do not have permission to update this blog."})

            if request.method == 'POST':
                title = request.POST.get('title')
                content = request.POST.get('content')

                blog.title = title
                blog.content = content
                blog.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'blog_{pk}',
                    {
                        'type': 'blog_update',
                        'title': blog.title,
                        'content': blog.content,
                        'likes': blog.likes
                    }
                )

                cache.delete('blog_list')

                return render(request, 'blog/blog_update.html', {"message": "Blog updated successfully!", 'blog': blog})

            return render(request, 'blog/blog_update.html', {'blog': blog})

        except AuthenticationFailed:
            return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})
    

def logout_view(request):
    response = redirect('login')
    response.delete_cookie('access_token')  
    cache.delete('access_token')
    logout(request)
    cache.delete('blog_list')
    cache.delete('user')
    cache.delete('blog_user_list_cache')
    # cache.delete('is_authenticated')
    # response.delete_cookie('is_authenticated')
    return response


@api_view(['GET','PUT'])
def blog_perm(request, pk, us_id, action):
    
        try:
            user =cache.get('user')

            blog = get_object_or_404(Blog, pk=pk)
            target_user = get_object_or_404(User, id=us_id)

            if blog.user_id == user.id:
                if action == 'grant':
                    blog.users_access.add(target_user)
                elif action == 'revoke':
                    blog.users_access.remove(target_user)
                cache.delete('blog_user_list_cache')
            return redirect('blog_detail', pk=pk)

        except AuthenticationFailed:
            return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})
    
@api_view(['GET','PUT'])
def blog_like(request,pk):
    
        try:
            user = cache.get('user')

            blog = get_object_or_404(Blog, pk=pk)

            if not(blog.users_who_liked.filter(id=user.id).exists()):
                blog.likes+=1
                blog.users_who_liked.add(user)
                print(blog.views)
                blog.save()
            else:
                blog.likes-=1
                blog.users_who_liked.remove(user)
                print(blog.views)
                blog.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'blog_{pk}',
                {
                    'type': 'blog_update',
                    'title': blog.title,
                    'content': blog.content,
                    'likes': blog.likes
                }
            )

            return redirect('blog_detail',pk=pk)

        except AuthenticationFailed:
            return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})
    
def blog_loading(request,pk):
        try:
            user = cache.get('user')

            blog = get_object_or_404(Blog, pk=pk)
            initial_like=blog.likes
            initial_title=blog.title
            initial_content=blog.content

            for _ in range(10):
                blog.refresh_from_db()
                if(blog.likes!= initial_like or blog.content!=initial_content or blog.title!=initial_title):
                    return JsonResponse({'likes':blog.likes,'content':blog.content,'title':blog.title})
            return JsonResponse({'likes':blog.likes,'content':blog.content,'title':blog.title})

        except AuthenticationFailed:
            return JsonResponse({"success":False})


@api_view(['GET','DELETE'])
def blog_delete(request, pk):
        try:
            user = cache.get('user')

            blog = get_object_or_404(Blog, pk=pk)

            if blog.user != user:
                return render(request, 'blog/blog_detail.html', {"error": "You do not have permission to delete this blog."})

            blog.delete()
            cache.delete('blog_list')
            return redirect('blog_list')

        except AuthenticationFailed:
            return redirect('/blog/login', {"error": "Authentication failed. Please log in again."})
    