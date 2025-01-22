from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



class User(AbstractUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)

    REQUIRED_FIELDS = ['email'] 

    def __str__(self):
        return self.email


class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    user = models.ForeignKey('blog.user', on_delete=models.CASCADE, related_name='blogs')
    views = models.IntegerField(default=0) 
    likes = models.IntegerField(default=0) 
    users_who_viewed = models.ManyToManyField('blog.user', related_name='viewed_blogs', blank=True)  
    users_who_liked = models.ManyToManyField('blog.user', related_name='liked_blogs', blank=True)
    users_access=  models.ManyToManyField('blog.user', related_name='useres_access', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title


# @receiver(post_save, sender=Blog)
# def blog_saved(sender, instance, **kwargs):
#     channel_layer = get_channel_layer()
#     blog_group = f'blog_{instance.pk}'
#     async_to_sync(channel_layer.group_send)(
#         blog_group,
#         {
#             'type': 'blog_update',
#             'title': instance.title,
#             'content': instance.content,
#             'likes': instance.likes,
#         }
#     )
