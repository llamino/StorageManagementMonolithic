# orders/forms.py

from django import forms
from dal import autocomplete
from .models import Order

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'shipping_address': autocomplete.ModelSelect2(
                url='address-autocomplete',
                forward=['user']
            )
        }
