from django.contrib import admin
from .models import Order, Customer, Product, OrderItem
# Register your models here.

admin.site.register([ Customer])

class OrderItemInline(admin.TabularInline): 
    model = OrderItem
    extra = 1 
    autocomplete_fields = ["product"]  
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
