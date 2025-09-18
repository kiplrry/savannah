# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import Order, Customer
from store.atsms import send_order_sms

@receiver(post_save, sender=Order)
def notify_customer_order_created(sender, instance: Order, created, **kwargs):
    if not created:
        return

    customer: Customer = instance.customer
    phone = customer.phone_number
    if not phone:
        print('no phone number')
        return
    # Format message (keep it short)
    print(instance.items.count())
    msg = (
        f"Hi {customer.name}, your order #{instance.id} was received.\n"
        f"Total: KES {instance.total_amount}\n"
        f"Items: {instance.items.count()}. Thanks!"
    )

    try:
        # res = send_order_sms(phone, msg)
        pass
        # print(f'ATS res: {res}')
    except Exception:
        print('exception occured')
        # swallow or log; don't crash order creation
        # we already logged in send_order_sms
        pass
