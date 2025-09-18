from rest_framework import serializers
from store.models import  Customer, Order, OrderItem, Product



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at", "id",]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "unit_price", "subtotal", "created_at"]
        read_only_fields = ["product_name", "unit_price", "subtotal", "created_at"]



class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "customer", "status", "total_amount", "items", "created_at", "updated_at"]
        read_only_fields = ['id', "customer", "status", "total_amount", "created_at", "updated_at"]


    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        customer: Customer = self.context["request"].customer
        print(f"customer: {customer}")
        
        order = Order.objects.create(customer=customer, **validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        order.update_total()

        from store.atsms import send_order_sms
        msg = (
            f"Hi {customer.name}, your order #{order.id} was received.\n"
            f"Total: KES {order.total_amount}\n"
            f"Items: {order.items.count()}. Thanks!"
        )
        try:
            send_order_sms(order, customer) # type: ignore
        except Exception as e:
            print("SMS failed:", e)

        return order   


    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", [])
        instance.status = validated_data.get("status", instance.status)
        instance.customer = validated_data.get("customer", instance.customer)
        instance.save()

        # 🔥 Simple approach: delete old items and recreate
        instance.items.all().delete()
        for item_data in items_data:
            OrderItem.objects.create(order=instance, **item_data)

        instance.update_total()
        return instance