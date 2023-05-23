from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .utils import SendNotificationMail
# Create your models here.
class Posts(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author', help_text="post created by user")
    title = models.CharField(max_length=200, help_text="title of post")
    body = models.TextField(help_text="description of post")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)



# send mail when new post is created
@receiver(post_save, sender=Posts)
def create_user_data(sender, instance, created, **kwargs):
    if created:
        try:
            subject = f"hii {instance.author.first_name} New Post Published"
            message = f'''Title:{instance.title} \n\n Body {instance.body}'''
            email = instance.author.email
            if settings.DEBUG:
                print(f'Mail Sent\n SUB:{subject}\n MESSAGE:{message}\n TO:{email}\n')
            else:
                SendNotificationMail(email, subject, message)
        except Exception as e:
            print("Signal Email Error", e)
        