# orders/urls.py

from django.urls import path, include
from orders.autocompletes import AddressAutocomplete
from orders.views import ListOrderItemView, CancelOrderView, CreateOrderView, UpdateOrderStatusView, ListUserOrdersView


urlpatterns = [
    path('admin-autocomplete/address/', AddressAutocomplete.as_view(), name='address-autocomplete'),
    path('list-order-items/<str:order_id>/', ListOrderItemView.as_view(), name='list-order-items'),
    path('cancel-order/', CancelOrderView.as_view(), name='cancel-order'),
    path('create-order/', CreateOrderView.as_view(), name='create-order'),
    path('update-order-status/', UpdateOrderStatusView.as_view(), name='update-order-status'),
    path('my-orders/', ListUserOrdersView.as_view(), name='list-user-orders'),
]
