import africastalking
from django.conf import settings
import logging
from .models import Order, Customer
from django.conf import settings

logger = logging.getLogger(__name__)

def initialize_atsdk():
    username = settings.ATSK_USERNAME
    api_key = settings.ATSK_API
    if not username or not api_key:
        raise RuntimeError("Africa's Talking credentials not configured (AT_USERNAME/AT_API_KEY)")
    sms = africastalking.SMSService(username, api_key)
    return sms

def send_order_sms(order:Order, customer: Customer = None, phone_number: str = None, message: str = None) -> dict:
    """
    Synchronously send an SMS via Africa's Talking.
    Returns provider response dict or raises exception on failure.
    """ 

    if not customer:
        customer = order.customer

    if customer and not phone_number:
        phone_number = customer.phone_number
    
    if not phone_number:
        raise RuntimeError("Phone Number missing")
    sms = initialize_atsdk()

    msg = message or (
            f"Hi {customer.name}, your order #{order.id} was received.\n"
            f"Total: KES {order.total_amount}\n"
            f"Items: {order.items.count()}. Thanks!"
        ) 
    try:
        # recipient must be in international format e.g. +2547XXXXXXXX
        response = sms.send(msg, [phone_number])
        logger.info("AT SMS sent: %s -> %s", phone_number, response)
        return response # type: ignore
    except Exception as e:
        logger.exception("Failed to send SMS via Africa's Talking")
        raise
