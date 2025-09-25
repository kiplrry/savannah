from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from store.models import Customer, Product, Order, OrderItem


class CustomerModelTest(TestCase):
    def test_customer_is_created_on_user_creation(self):
        user = User.objects.create(username="alice")
        customer = Customer.objects.get(user=user)
        self.assertIsNotNone(customer)
        self.assertEqual(customer.name, "alice")
        self.assertEqual(str(customer), f"{customer.name} ID: {customer.id}")



class ProductModelTest(TestCase):
    def test_str_representation_with_code(self):
        product = Product.objects.create(name="Widget", code="P001", price=Decimal("10.00"))
        self.assertEqual(str(product), "Widget - P001")

    def test_str_representation_without_code(self):
        product = Product.objects.create(name="Gadget", price=Decimal("5.00"))
        self.assertEqual(str(product), "Gadget - ")


class OrderModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="bob")
        self.customer = Customer.objects.get(user=user)
        self.product1 = Product.objects.create(name="Widget", code="P001", price=Decimal("10.00"))
        self.product2 = Product.objects.create(name="Gadget", code="P002", price=Decimal("5.00"))

    def test_str_representation_and_initial_total(self):
        order = Order.objects.create(customer=self.customer)
        self.assertEqual(order.total_amount, Decimal("0.00"))
        self.assertEqual(str(order), f"Order #{order.id} - {self.customer.name}")

    def test_update_total_with_items(self):
        order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(order=order, product=self.product1, quantity=2, unit_price=self.product1.price)
        OrderItem.objects.create(order=order, product=self.product2, quantity=1, unit_price=self.product2.price)

        order.refresh_from_db()
        self.assertEqual(order.total_amount, Decimal("25.00"))


class OrderItemModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username="charlie")
        self.customer = Customer.objects.get(user=user)
        self.product = Product.objects.create(name="Thing", code="P003", price=Decimal("7.50"))
        self.order = Order.objects.create(customer=self.customer)

    def test_str_representation_and_subtotal(self):
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=3, unit_price=self.product.price)
        item.save()

        self.assertEqual(str(item), f"{self.product.name} x 3")
        self.assertEqual(item.subtotal, Decimal("22.50"))

        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("22.50"))

    def test_delete_item_updates_order_total(self):
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, unit_price=10)
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("20.00"))

        item.delete()
        self.order.refresh_from_db()
        self.assertEqual(self.order.total_amount, Decimal("0.00"))
