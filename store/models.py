from django.contrib.auth.models import User
from django.db import models
from decimal import Decimal
from django.core.exceptions import ValidationError


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer_profile", help_text="Only staff can set this. For normal users, it is auto-filled.")
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, help_text="Only staff can set this. For normal users, it is auto-filled.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ID: {self.id}" # type: ignore


class Product(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.code or ''}"
    

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def save(self, *args, **kwargs):
        self.full_clean()  # runs clean()
        super().save(*args, **kwargs)
    
class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal(0.00))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}" # type: ignore

    def update_total(self):
        total = sum(item.subtotal for item in self.items.all()) # type: ignore
        if total < 0:
            total = 0
        self.total_amount = total
        self.save()



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.unit_price is None and self.product_id:
            self.unit_price = self.product.price
        if self.subtotal is None and self.unit_price is not None and self.quantity is not None:
            self.subtotal = self.unit_price * self.quantity
        self.subtotal = self.quantity * self.unit_price

        self.full_clean()

        super().save(*args, **kwargs)

        self.order.update_total()
    
    def delete(self, *args, **kwargs):
        order = self.order 
        super().delete(*args, **kwargs)
        order.update_total()

    def clean(self):
        if self.unit_price < 0:
            raise ValidationError("Unit price cannot be negative.")
        
        if self.subtotal < 0:
            raise ValidationError("Subtotal cannot be negative.")

        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be greater than zero."})


    def __str__(self):
        return f"{self.product.name} x {self.quantity}"