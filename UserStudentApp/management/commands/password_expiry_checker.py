from django.core.management.base import BaseCommand, CommandError
from UserStudentApp.models import CustomUser
from datetime import date, timedelta
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Checks password expiry for all the users.'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        subject = 'Password Expiry Notification'

        for user in users:
            time_left = date.today() - user.password_change_date
            if user.is_superuser:
                continue
            elif time_left > timedelta(days=6) and time_left < timedelta(days=10):
                user.is_blocked = False
                print(user.email)
                user.save()
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                link = 'localhost:8000/reset/'+uid+'/'+token
                message = "Your password is about to expire in {days} days."\
                    "Please use the following link to change your password.".format(days=timedelta(days=10)-time_left)
                # send_mail(subject, message, 'admin@django.com', ['itsrealboy1@gmail.com'])
            elif time_left > timedelta(days=9):
                user.is_blocked = True
                user.save()
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                link = 'localhost:8000/reset/'+uid+'/'+token
                message = "Your password expiry date has crossed the limit due to which your account has been BLOCKED."\
                    "Use the following link to unblock your account.\n" + link
                # send_mail(subject, message, 'admin@django.com', ['itsrealboy1@gmail.com'])
            else:
                user.is_blocked=False
                user.save()