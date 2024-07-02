from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Group

@receiver(post_save, sender=User)
def create_default_groups(sender, instance, created, **kwargs):
    if created:
        Group.objects.create(name='Family', creator=instance)
        Group.objects.create(name='Friends', creator=instance)
        Group.objects.create(name='Work', creator=instance)
