from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Cart, CartItem, Item, Order, OrderItem, Transaction


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ItemSerializer(serializers.ModelSerializer):
    item_id = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = ["item_id", "name", "price", "status"]

    def get_item_id(self, obj):
        return obj.id


class CartItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = CartItem
        fields = ["item", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    cart_id = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    items = CartItemSerializer(source="cartitem_set", many=True)

    class Meta:
        model = Cart
        fields = ["cart_id", "user_id", "username", "items", "total_price"]

    def get_user_id(self, obj):
        return obj.user.id

    def get_cart_id(self, obj):
        return obj.id

    def get_username(self, obj):
        return obj.user.username

    def get_total_price(self, obj):
        return obj.total_price


class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = OrderItem
        fields = ["item", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.SerializerMethodField()
    items = OrderItemSerializer(source="orderitem_set", many=True)

    class Meta:
        model = Order
        fields = ["order_id", "user", "items", "total_amount", "is_paid"]

    def get_order_id(self, obj):
        return obj.id


class PlaceOrderSerializer(serializers.ModelSerializer):
    place_order = serializers.BooleanField()

    class Meta:
        model = Order
        fields = ["place_order"]


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "user", "total_amount", "is_paid"]
        read_only_fields = fields


class PayOrderSerializer(serializers.ModelSerializer):
    pay = serializers.BooleanField()

    class Meta:
        model = Transaction
        fields = ["pay"]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
