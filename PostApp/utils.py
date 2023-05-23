
from django.core.mail import send_mail
from django.conf import settings
def SendNotificationMail(email, subject, message):
    try:
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list)
    except Exception as e:
        print("Error Email", e)