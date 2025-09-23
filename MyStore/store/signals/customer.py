from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models import Customer


@receiver(post_save, sender=User)
def sync_customer_with_user(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(
            user=instance,
            name=instance.get_full_name() or instance.username,
            email=instance.email,
        )
    else:
        # for updates
        try:
            customer = instance.customer_profile
            customer.name = instance.get_full_name() or instance.username
            customer.email = instance.email
            customer.save()
        except Customer.DoesNotExist:
            # Recereate if customer profile does not exist
            Customer.objects.create(
                user=instance,
                name=instance.get_full_name() or instance.username,
                email=instance.email,
            )
