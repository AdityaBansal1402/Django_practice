from celery import shared_task
from django.core.mail import send_mail

@shared_task(name='blog.views.mail_send')
def mail_send(blog_title, blog_views, user_email):
    send_mail(
        subject='Your blog reached a milestone!',
        message=f'Your blog "{blog_title}" has reached {blog_views} views!',
        from_email='adityabansal3009@gmail.com',
        recipient_list=[user_email],
        fail_silently=False,
    )