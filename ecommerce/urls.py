from django.urls import path
from . import views

urlpatterns = [
    # General endpoints
    path("", views.get_endpoints, name="get-endpoints"),
    path("health-check/", views.health_check, name="health-check"),
    # User endpoints
    path("user/", views.UserView.as_view(), name="user-list-create"),
    path("user/<str:username>/", views.UserView.as_view(), name="user-detail-delete"),
    # Cart endpoints
    path("cart/", views.CartAPIView.as_view(), name="cart-get-post-delete"),
    # Order endpoints
    path("order/", views.OrderView.as_view(), name="order-list-create"),
    path("order/<int:order_id>/", views.OrderView.as_view(), name="order-detail"),
    # Payment
    path("pay_order/<int:order_id>/", views.PayOrderView.as_view(), name="pay_order"),
]
