import pytest
from unittest.mock import patch
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from store.models import Customer, Product, Order, OrderItem
from ..serializers import CustomerSerializer, ProductSerializer, OrderItemSerializer, OrderSerializer
from django.db import transaction


@pytest.mark.django_db
class TestCustomerSerializer:
    def test_email_readonly_for_normal_user(self):
        user = User.objects.create_user(username="alice")
        customer =  user.customer_profile
        request = APIRequestFactory().get("/")
        request.user = user

        serializer = CustomerSerializer(customer, context={"request": request})
        fields = serializer.get_fields()
        assert fields["email"].read_only is True

    def test_email_writable_for_staff(self):
        staff = User.objects.create_user(username="admin", is_staff=True)
        customer = staff.customer_profile
        request = APIRequestFactory().get("/")
        request.user = staff

        serializer = CustomerSerializer(customer, context={"request": request})
        fields = serializer.get_fields()
        assert fields["email"].read_only is False


@pytest.mark.django_db
class TestOrderItemSerializer:
    def test_create_sets_unit_price_and_subtotal(self):
        product = Product.objects.create(name="Widget", code="W1", price=Decimal("10.00"))
        user = User.objects.create(username="bob")
        customer = user.customer_profile
        order = Order.objects.create(customer=customer)

        data = {
            "product": product.id, 
            "order": order.id,
            "quantity": 2
        }
        serializer = OrderItemSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

        item = serializer.save(order=order)
        assert item.unit_price == Decimal("10.00")
        assert item.subtotal == Decimal("20.00")


    def test_update_quantity_recalculates_subtotal(self):
        product = Product.objects.create(name="Widget", code="W2", price=Decimal("5.00"))
        user=User.objects.create(username="sam")
        customer = user.customer_profile
        order = Order.objects.create(customer=customer)
        item = OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=5, subtotal=5)

        serializer = OrderItemSerializer(item, data={"quantity": 3}, partial=True)
        assert serializer.is_valid(), serializer.errors
        updated = serializer.save()

        assert updated.quantity == 3
        assert updated.subtotal == Decimal("15.00")


@pytest.mark.django_db
class TestOrderSerializer:
    def test_normal_user_cannot_set_customer(self):
        user = User.objects.create_user(username="joe")
        customer = user.customer_profile
        product = Product.objects.create(name="Widget", code="W3", price=Decimal("20.00"))

        request = APIRequestFactory().post("/")
        request.user = user
        request.customer = customer

        data = {
            "customer": customer.id,
            "items": [{"product": product.id, "quantity": 2}],
        }
        serializer = OrderSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        order = serializer.save()

        # Customer should be injected from request, not payload
        assert order.customer == customer
        assert order.total_amount == Decimal("40.00")
    

    def test_admin_can_set_customer_and_status(self):
        staff = User.objects.create_user(username="admin", is_staff=True)
        customer = staff.customer_profile
        product = Product.objects.create(name="Gadget", code="G1", price=Decimal("15.00"))

        request = APIRequestFactory().post("/")
        request.user = staff

        data = {
            "customer": customer.id,
            "status": "completed",
            "items": [{"product": product.id, "quantity": 1}],
        }
        serializer = OrderSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        order = serializer.save()

        assert order.customer == customer
        assert order.status == "completed"
        assert order.total_amount == Decimal("15.00")

    @pytest.mark.django_db(transaction=True)
    @patch("api.serializers.send_order_sms")  
    def test_sms_sent_after_customer_creates_order(self, mock_send_sms):
        user = User.objects.create_user(username="joe")
        customer: Customer = user.customer_profile
        customer.phone_number = "+254795058569"
        customer.save()
        product = Product.objects.create(name="Widget", code="W3", price=Decimal("20.00"))

        request = APIRequestFactory().post("/")
        request.user = user
        request.customer = customer
        data = {
            "items": [{"product": product.id, "quantity": 2}],
        }

        serializer = OrderSerializer(data=data, context={"request": request})

        assert serializer.is_valid(), serializer.errors
        order = serializer.save()

        assert order.customer == customer
        assert order.total_amount == Decimal("40.00")

        mock_send_sms.assert_called_once_with(order, customer)