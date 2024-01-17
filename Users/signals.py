from django.contrib.auth.models import User
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=User)
def createProfile(sender, instance, created, **kwargs):

    if created:
        user = instance
        Profile.objects.create(
            user=user,
        )


@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):

    try:
        instance.user.delete()
    except Exception as e:
        print(f'{e} raised during deleting user')
