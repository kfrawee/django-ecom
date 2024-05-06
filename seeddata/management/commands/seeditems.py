# seeddata/management/commands/seed_items.py
from django.core.management.base import BaseCommand
from ecommerce.models import Item
import random


class Command(BaseCommand):
    help = "Seed items into the database"
    status_choices = ("Pending", "Accepted")

    def handle(self, *args, **kwargs):
        for i in range(10):
            Item.objects.get_or_create(
                name=f"item{i}",
                description=f"Description for item{i}",
                price=random.choice(range(10, 1000)) / 10,
                status=random.choice(self.status_choices),
            )

        self.stdout.write(self.style.SUCCESS(f"All items created successfully - {Item.objects.count()}"))
