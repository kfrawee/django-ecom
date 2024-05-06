from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


from ecommerce.models import Cart


class Command(BaseCommand):
    help = "Seed users into the database"

    def handle(self, *args, **kwargs):
        for i in range(10):
            User.objects.get_or_create(username=f"user{i}", password=f"password{i}")
            if i == 0:
                # create cart
                cart, _ = Cart.objects.get_or_create(user=User.objects.get(username="user0"))
        self.stdout.write(
            self.style.SUCCESS(f"All users created successfully - {User.objects.filter(is_staff=False).count()}")
        )
