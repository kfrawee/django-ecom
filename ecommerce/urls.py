from django.urls import path
from . import views

urlpatterns = [
    # General endpoints
    path("health-check/", views.health_check, name="health-check"),
    # User endpoints
    path(
        "user/", views.UserView.as_view(), name="user-create"
    ),  # POST method for creating a user
    path("user/<str:username>/", views.UserView.as_view(), name="user-detail-delete"),
    # Cart endpoints
    path("cart/", views.get_cart, name="get-cart"),
    path("cart/add-item/", views.add_item_to_cart, name="add-item-to-cart"),
    # Order endpoints
    path("my-orders/", views.get_my_orders, name="get-my-orders"),
    path("order-detail/<int:id>/", views.get_order_detail, name="get-order-detail"),
    path("order/", views.create_order, name="create-order"),
    path("pay-order/<int:id>/", views.pay_order, name="pay-order"),
    # Item endpoints
    path("add-item/", views.add_item, name="add-item"),
]
