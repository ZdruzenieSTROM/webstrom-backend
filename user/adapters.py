from allauth.account.adapter import DefaultAccountAdapter
from django.core.mail import send_mail
from webstrom.settings import EMAIL_NO_REPLY


class CustomAccountAdapter(DefaultAccountAdapter):

    def send_mail(self, template_prefix, email, context):
        # Táto funkcia by mala poslať email s linkom na aktiváciu. Na to je ale potrebné mať na
        # na frontende stránku, ktorá z linku vyextrahuje 'key' a pošle ho na api endpoint
        # zabezpečujúci aktiváciu. Zatiaľ tento 'key' je len priložený v tele emailu

        # Api endpoint na aktiváciu: /user/registration/verify-email/

        # Na znení mailu sa dohodneme neskôr

        send_mail(
            'Konfirmácia emailovej adresy',
            f'Key = {context["key"]}',
            EMAIL_NO_REPLY,
            [context['user'].email]
        )
