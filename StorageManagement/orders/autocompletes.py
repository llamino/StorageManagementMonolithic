# orders/autocompletes.py
from dal import autocomplete
from users.models import Address

class AddressAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Address.objects.none()  # محافظت در برابر دسترسی عمومی

        qs = Address.objects.all()
        user_id = self.forwarded.get('user')
        if user_id:
            qs = qs.filter(user_id=user_id)
        return qs
