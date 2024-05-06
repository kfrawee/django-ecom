from functools import wraps

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, Item, Order, Transaction
from .serializers import (
    CartSerializer,
    PayOrderSerializer,
    OrderSerializer,
    TransactionSerializer,
    OrderListSerializer,
    UserCreateSerializer,
    PlaceOrderSerializer,
)
from .utils import bypass_user_auth_decorator


def bypass_user_auth_decorator(method):
    def bypass_user_auth(request):
        """For testing only, replace "admin" or assume user0 is logged in"""
        try:
            user = User.objects.get(username="user0")
            request.user = user
        except User.DoesNotExist:
            log_msg = "Please run `python manage.py seedusers` first"
            raise Exception(log_msg)

        return request

    @wraps(method)
    def wrapper(self, request, *args, **kwargs):
        request = bypass_user_auth(request)
        return method(self, request, *args, **kwargs)

    return wrapper


@api_view(["GET"])
def health_check(request):
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def get_endpoints(request):
    from django.urls import get_resolver

    all_endpoints = get_resolver().url_patterns
    ecommerce_endpoints = all_endpoints[1].url_patterns
    return Response({"all_endpoints": [repr(endpoint) for endpoint in ecommerce_endpoints]})


class UserView(APIView):
    serializer_class = UserCreateSerializer

    def get(self, _, username=None):
        if not username:
            all_usernames = [user.username for user in User.objects.all() if not user.is_staff]
            return Response({"registered_user": all_usernames})
        try:
            user = User.objects.get(username=username)
            serializer = UserCreateSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _, username):
        try:
            user = User.objects.get(username=username)
            user.delete()
            return Response({"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)


class CartAPIView(APIView):
    @bypass_user_auth_decorator
    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cartitem_set.select_related("item").all()
        if not cart_items.exists():
            return Response(
                "User has no items in cart. Add items to cart first. use /add-item",
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @bypass_user_auth_decorator
    def post(self, request):
        item = Item.objects.get(id=request.data.get("item_id"))
        quantity = request.data.get("quantity", 1)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.add_item(item, quantity)
        return Response(status=status.HTTP_200_OK)

    @bypass_user_auth_decorator
    def delete(self, request):
        cart = Cart.objects.get(user=request.user)
        cart.empty_cart()
        cart.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderView(APIView):
    def get_serializer(self):
        if self.kwargs.get("order_id"):
            return OrderListSerializer()
        return PlaceOrderSerializer()

    @bypass_user_auth_decorator
    def get(self, request, order_id=None):
        if not order_id:
            orders = Order.objects.filter(user=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        else:
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            except Order.DoesNotExist:
                return Response({"message": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)

    @bypass_user_auth_decorator
    def post(self, request, order_id=None):
        serializer = PlaceOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if order_id:
            return Response(
                {"message": "Cannot place an order from an order detail. Use /order instead"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.data.get("place_order"):
            return Response(
                {"message": "Cannot create order without placing an order"}, status=status.HTTP_400_BAD_REQUEST
            )

        cart = Cart.objects.get(user=request.user)
        try:
            order = Order.create_order(request.user, cart)
        except ValueError:
            return Response(
                {"message": "Cannot create order: There are no accepted items in the cart"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PayOrderView(APIView):
    serializer_class = PayOrderSerializer

    @bypass_user_auth_decorator
    def post(self, request, order_id=None):
        serializer = PayOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("pay"):
            return Response({"message": "Cannot pay order without paying"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"message": "Order does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if order.is_paid:
            return Response({"message": "Order is already paid"}, status=status.HTTP_400_BAD_REQUEST)

        Transaction.objects.create(order=order, amount=order.total_amount, success=True)
        return Response("Order paid successfully", status=status.HTTP_200_OK)
