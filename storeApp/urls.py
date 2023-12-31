from django.urls import path
from . import views


urlpatterns = [
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('orders/', views.orders, name="orders"),
    path('view/<int:product_id>/', views.view, name="view"),
    path('login/', views.login, name="login"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.ProcessOrder, name="process_order"),
    path('', views.store, name="store"),
]