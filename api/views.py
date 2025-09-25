from rest_framework import  viewsets, permissions
from .serializers import  CustomerSerializer, OrderItemSerializer, ProductSerializer, OrderSerializer
from store.models import Customer, Order, OrderItem, Product
from drf_spectacular.utils import extend_schema


class IsAdminOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.customer.user == request.user
    
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    SAFE methods (GET, HEAD, OPTIONS) → allowed for everyone.
    Write methods (POST, PUT, PATCH, DELETE) → only for staff/admin.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
    
class IsStaff(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return False
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaff]
    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user=self.request.user)
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny & IsAdminOrReadOnly]

    @extend_schema(
        description="List products (all users). Only admin can create/update/delete."
    )
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related("customer", "customer__user")
        return Order.objects.filter(customer__user=self.request.user).select_related("customer", "customer__user")


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related("order__customer", "product")
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.select_related("order__customer", "product")
        return OrderItem.objects.filter(order__customer__user=self.request.user).select_related("order__customer", "product")
