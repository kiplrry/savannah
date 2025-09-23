from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
# urls.py
from rest_framework_nested import routers

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)

# nested router for order items
orders_router = routers.NestedDefaultRouter(router, r'orders', lookup='order')
orders_router.register(r'items', views.OrderItemViewSet, basename='order-items')

urlpatterns = [
    path("", include(router.urls)),
    path("", include(orders_router.urls)),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/swagger/", SpectacularSwaggerView.as_view(url_name="schema")),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema")),

]


