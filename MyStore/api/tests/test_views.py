import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from store.models import Customer, Order
from ..views import IsAdminOrOwner, IsAdminOrReadOnly, IsStaff


@pytest.mark.django_db
class TestIsAdminOrOwner:
    def test_admin_has_access(self):
        staff = User.objects.create_user(username="admin", is_staff=True)
        request = APIRequestFactory().get("/")
        request.user = staff

        perm = IsAdminOrOwner()
        assert perm.has_object_permission(request, None, object()) is True

    def test_owner_has_access(self):
        user = User.objects.create_user(username="bob")
        customer = user.customer_profile
        order = Order.objects.create(customer=customer)

        request = APIRequestFactory().get("/")
        request.user = user

        perm = IsAdminOrOwner()
        assert perm.has_object_permission(request, None, order) is True

    def test_other_user_denied(self):
        user1 = User.objects.create_user(username="alice")
        customer1 = user1.customer_profile 
        order = Order.objects.create(customer=customer1)

        user2 = User.objects.create_user(username="bob")
        request = APIRequestFactory().get("/")
        request.user = user2

        perm = IsAdminOrOwner()
        assert perm.has_object_permission(request, None, order) is False


@pytest.mark.django_db
class TestIsAdminOrReadOnly:
    def test_safe_methods_allowed_for_anyone(self):
        request = APIRequestFactory().get("/")
        request.user = User.objects.create_user(username="joe")

        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is True

    def test_write_denied_for_normal_user(self):
        request = APIRequestFactory().post("/")
        request.user = User.objects.create_user(username="joe")

        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is False

    def test_write_allowed_for_admin(self):
        staff = User.objects.create_user(username="admin", is_staff=True)
        request = APIRequestFactory().post("/")
        request.user = staff

        perm = IsAdminOrReadOnly()
        assert perm.has_permission(request, None) is True


@pytest.mark.django_db
class TestIsStaff:
    def test_staff_has_access(self):
        staff = User.objects.create_user(username="admin", is_staff=True)
        request = APIRequestFactory().get("/")
        request.user = staff

        perm = IsStaff()
        assert perm.has_object_permission(request, None, object()) is True

    def test_normal_user_denied(self):
        user = User.objects.create_user(username="bob")
        request = APIRequestFactory().get("/")
        request.user = user

        perm = IsStaff()
        assert perm.has_object_permission(request, None, object()) is False
