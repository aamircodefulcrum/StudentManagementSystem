from django.core.management.base import BaseCommand
from UserStudentApp.models import CustomUser
from datetime import date, timedelta
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
            elif timedelta(days=6) < time_left < timedelta(days=10):
                print("Email sent to", user.email)
                link = 'localhost:8000/change_password/'
                message = "Your password is about to expire in {}. "\
                    "Please use the following link to change your password.\n".format(timedelta(days=10)-time_left)
                send_mail(subject, message + link, 'admin@django.com', ['itsrealboy1@gmail.com'])
            elif time_left > timedelta(days=9):
                print(user.username, "is Blocked")
                user.is_blocked = True
                user.save()
                link = 'localhost:8000/change_password/'
                message = "Your password expiry date has crossed the limit due to which your account has been BLOCKED."\
                    "Use the following link to unblock your account.\n" + link
                send_mail(subject, message, 'admin@django.com', ['itsrealboy1@gmail.com'])
            else:
                user.is_blocked = False
                user.save()
