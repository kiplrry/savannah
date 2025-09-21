from rest_framework import serializers
from store.models import  Customer, Order, OrderItem, Product
from drf_spectacular.utils import extend_schema_serializer, OpenApiExample
from django.db import transaction



@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Normal user ",
            summary="Normal User",
            value={
                "name": "string",
                "phone_number": "string",
            },
        ),
        OpenApiExample(
            "Admin/staff",
            summary="Admin/staff",
            value={
                "name": "string",
                "phone_number": "string",
                "email": "user@example.com",
            },
        ),
    ]
)
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        fields["user"].read_only = True

        if request and not request.user.is_staff:
            fields["email"].read_only = True
            
        return fields

@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Read-only for normal users",
            value={"id": 1, "name": "Widget", "code": "P001", "price": "10.00"},
            summary="Normal users can only read products"
        ),
        OpenApiExample(
            "Admin create product",
            value={"name": "Widget", "code": "P001", "price": "10.00"},
            summary="Only admins can create products"
        ),
    ]
)
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    unit_price = serializers.DecimalField(
        source="product.price", 
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",        # user picks product by ID
            "product_name",   # show product name
            "quantity",       # user can change quantity
            "unit_price",     # auto-set from product
            "subtotal",       # calculated (qty * price)
            "created_at",
        ]
        read_only_fields = ["product_name", "unit_price", "subtotal", "created_at"]

    def create(self, validated_data):
        """Ensure unit_price and subtotal are always correct."""
        product = validated_data["product"]
        quantity = validated_data.get("quantity", 1)

        return OrderItem.objects.create(
            product=product,
            order=validated_data["order"],
            quantity=quantity,
            unit_price=product.price,
            subtotal=product.price * quantity,
        )

    def update(self, instance, validated_data):
        """Allow updating only quantity; recalc subtotal."""
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.unit_price = instance.product.price
        instance.subtotal = instance.unit_price * instance.quantity
        instance.save()
        return instance

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value




@extend_schema_serializer(
    examples=[
        OpenApiExample(
            "Normal user order",
            summary="Normal user cannot set customer",
            value={
                "items": [{"product": 1, "quantity": 2}],
            },
        ),
        OpenApiExample(
            "Admin order",
            summary="Admin can set customer",
            value={
                "customer": 5,
                "items": [{"product": 1, "quantity": 2}],
            },
        ),
    ]
)
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "status", "total_amount", "items", "created_at", "updated_at"]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        if request and not request.user.is_staff:
            # Normal users → cannot set customer, status, or total_amount
            fields["customer"].read_only = True
            fields["status"].read_only = True
            fields["total_amount"].read_only = True

        return fields


    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        request = self.context["request"]

        if request.user.is_staff:
            customer = validated_data.pop("customer")
        else:
            customer = request.customer

        order = Order.objects.create(customer=customer, **validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.update_total()

        from store.atsms import send_order_sms
        try:
            transaction.on_commit(lambda: send_order_sms(order, customer))
        except Exception as e:
            print("SMS failed:", e)

        return order

    def update(self, instance, validated_data):
        request = self.context["request"]

        if request.user.is_staff:
            instance.customer = validated_data.get("customer", instance.customer)
            instance.status = validated_data.get("status", instance.status)

        items_data = validated_data.pop("items", [])
        existing_items = {item.product_id: item for item in instance.items.all()}

        # Track products seen in the request
        updated_product_ids = set()

        for item_data in items_data:
            product = item_data["product"]
            product_id = product.id if hasattr(product, "id") else product
            updated_product_ids.add(product_id)

            if product_id in existing_items:
                # update quantity & unit price
                existing_item = existing_items[product_id]
                existing_item.quantity = item_data.get("quantity", existing_item.quantity)
                existing_item.unit_price = item_data.get("unit_price", existing_item.unit_price)
                existing_item.save()
            else:
                # create new item
                OrderItem.objects.create(order=instance, **item_data)

        # delete items that were not in the new payload
        for product_id, item in existing_items.items():
            if product_id not in updated_product_ids:
                item.delete()

        instance.save()
        instance.update_total()
        return instance
