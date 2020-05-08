from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.apps import apps


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        apps.get_model('GBEX_app', 'Profile').objects.create(user=instance, table_settings="{}")
