from django.contrib import admin
from .models import Item, Cart, CartItem, Order, OrderItem, Transaction


class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "price", "status")
    list_filter = ("status",)
    search_fields = ("name", "description")


admin.site.register(Item, ItemAdmin)


class CartItemInline(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ("user",)
    inlines = [CartItemInline]
    search_fields = ("user__username__icontains",)

    def has_add_permission(self, request):
        return False


admin.site.register(Cart, CartAdmin)


class OrderItemInline(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "total_amount", "is_paid")
    inlines = [OrderItemInline]
    search_fields = ("user__username__icontains",)

    def has_add_permission(self, request):
        return False


admin.site.register(Order, OrderAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "timestamp", "transaction_id", "success")
    search_fields = ("order__user__username__icontains",)
    # only allow change status
    readonly_fields = list_display[:-1]

    def has_add_permission(self, request):
        return False


admin.site.register(Transaction, TransactionAdmin)
