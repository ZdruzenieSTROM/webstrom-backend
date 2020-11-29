from django.db.models.signals import post_save

from user.models import User
from personal.models import Profile


def callback(sender, instance, **kwargs):
    # pylint: disable=W0613

    Profile.objects.get_or_create(
        user=instance, defaults={'year_of_graduation': 2000,
                                 'school_id': 1, 'first_name': '', 'last_name': ''})
    instance.profile.save()


post_save.connect(callback, sender=User)
