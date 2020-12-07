# from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        print("--------------------")
        print("Email poslany. Urcite???")
        print("--------------------")
