from django.http import HttpRequest
from store.models import Customer

class CustomerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if request.user.is_authenticated:
            customer, _ = Customer.objects.get_or_create(user=request.user)
            request.customer = customer
        else:
            request.customer = None
        return self.get_response(request)
