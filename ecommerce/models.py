import uuid
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    status_choices = [("Pending", "Pending"), ("Accepted", "Accepted")]
    status = models.CharField(max_length=10, choices=status_choices, default="Pending")

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Item, through="CartItem")

    def __str__(self):
        return f"Cart of {self.user.username}"

    def add_item(self, item, quantity=1):
        cart_item, created = CartItem.objects.get_or_create(cart=self, quantity=quantity, item=item)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

    def empty_cart(self):
        self.items.clear()

    @property
    def total_price(self):
        total = sum(
            cart_item.quantity * cart_item.item.price
            for cart_item in self.cartitem_set.all()
            if cart_item.item.status == "Accepted"
        )
        return total


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in Cart of {self.cart.user.username}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} - {self.user.username}"

    @classmethod
    def create_order(cls, user, cart):
        # Get all accepted items in the cart
        accepted_items = cart.cartitem_set.filter(item__status="Accepted")

        # Check if there are any accepted items
        if not accepted_items.exists():
            raise ValueError("Cannot create order: There are no accepted items in the cart")

        order = cls.objects.create(user=user, cart=cart, total_amount=cart.total_price)

        # Create order items
        for cart_item in accepted_items:
            OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity)

        # Remove accepted items from cart
        cart.items.remove(*[cart_item.item for cart_item in accepted_items])

        return order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in Order {self.order.id}"


class Transaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True, default=str(uuid.uuid4()))
    success = models.BooleanField(default=False)

    def __str__(self):
        return f"Transaction {self.transaction_id} for Order {self.order.id}, Amount: {self.amount}, Success: {self.success}"


@receiver(post_save, sender=Transaction)
def update_order_status(sender, instance, created, **kwargs):
    if instance.success and not instance.order.is_paid:
        instance.order.is_paid = True
        instance.order.save()
