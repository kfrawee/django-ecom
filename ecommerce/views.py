from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Cart, Item, Order, Transaction
from .serializers import (
    CartSerializer,
    EndpointSerializer,
    ItemSerializer,
    OrderSerializer,
    TransactionSerializer,
    UserCreateSerializer,
)


@api_view(["GET"])
def health_check(request):
    return Response(status=status.HTTP_200_OK)


class UserView(APIView):
    serializer_class = UserCreateSerializer

    def get(self, request, username=None):
        if not username:
            all_usernames = [
                user.username for user in User.objects.all() if not user.is_staff
            ]
            return Response({"usernames": all_usernames})
        try:
            user = User.objects.get(username=username)
            serializer = UserCreateSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, username):
        try:
            user = User.objects.get(username=username)
            user.delete()
            return Response(
                {"message": "User deleted"}, status=status.HTTP_204_NO_CONTENT
            )
        except User.DoesNotExist:
            return Response(
                {"message": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


# Views for the specified endpoints
@api_view(["GET"])
def get_cart(request):
    cart = Cart.objects.get(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(["GET"])
def get_my_orders(request):
    orders = Order.objects.filter(user=request.user, is_paid=True)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_order_detail(request, id):
    order = Order.objects.get(id=id, user=request.user, is_paid=True)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(["POST"])
def add_item(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_item_to_cart(request):
    cart = Cart.objects.get(user=request.user)
    item = Item.objects.get(id=request.data.get("item_id"))
    quantity = request.data.get("quantity", 1)
    cart.add_item(item, quantity)
    return Response(status=status.HTTP_200_OK)


@api_view(["POST"])
def create_order(request):
    cart = Cart.objects.get(user=request.user)
    order = Order.create_order(request.user, cart)
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def pay_order(request, id):
    order = Order.objects.get(id=id, user=request.user)
    Transaction.objects.create(order=order, amount=order.total_amount, success=True)
    order.is_paid = True
    order.save()
    return Response(status=status.HTTP_200_OK)
