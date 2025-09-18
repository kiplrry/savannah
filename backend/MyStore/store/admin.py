from django.contrib import admin
from .models import Order, Customer, Product, OrderItem
# Register your models here.

admin.site.register([ Customer])

class OrderItemInline(admin.TabularInline):  # or admin.StackedInline for bigger forms
    model = OrderItem
    extra = 1  # how many empty rows to show by default
    autocomplete_fields = ["product"]  # nice dropdown for product
    readonly_fields = [ "subtotal", "created_at"]

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["customer__name"]
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "unit_price", "subtotal"]
    list_filter = ["created_at"]
    search_fields = ["product__name", "order__customer__name"]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "created_at"]
    search_fields = ["name"]
