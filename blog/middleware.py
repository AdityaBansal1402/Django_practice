from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.core.cache import cache

class JWTAuthenticationMiddleware:
    """
    Middleware to check JWT authentication on every request, except during registration.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path not in ['/blog/', '/blog/login/']and not request.path.startswith('/accounts/'):
            token = cache.get('access_token')  
            oauth=request.user.is_authenticated
            if(not token):
                token = request.COOKIES.get('access_token')   

            if token:
                try:
                    # print(token)
                    cache.set('access_token',token,timeout=60*5)
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(token)
                    user = jwt_auth.get_user(validated_token)
                    request.user = user  
                    cache.set('user',user,timeout=60*50)
                except AuthenticationFailed:
                    response = redirect('login')
                    response.delete_cookie('access_token')  
                    cache.delete('access_token')
                    return response 
            elif oauth:
                cache.set('is_authenticated',True,timeout=60*5)
            
            else:
                return redirect('login')
        response = self.get_response(request)
        return response
