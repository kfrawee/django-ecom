# seeddata/management/commands/seed_items.py
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
import random
from ecommerce.models import Cart, Item


class Command(BaseCommand):
    help = "Seed items to user0's cart"

    def handle(self, *args, **kwargs):
        user = User.objects.get(username="user0")
        cart = Cart.objects.get(user=user)
        if not Item.objects.exists():
            log_msg = "Please run `python manage.py seeditems` first"
            raise Exception(log_msg)

        cart_items = cart.cartitem_set.select_related("item").all()
        if not (cart_items.exists() and len(cart_items) == 3):
            for i in range(3):
                item = Item.objects.get(id=i + 1)
                quantity = random.randint(1, 10)
                cart.add_item(item, quantity)

        self.stdout.write(self.style.SUCCESS(f"Cart of {user.username} created successfully"))
