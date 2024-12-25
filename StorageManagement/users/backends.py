
from django.contrib.auth.backends import ModelBackend
class CustomAuthenticationBackend(ModelBackend):
    def user_can_authenticate(self, user):
        # اضافه کردن شرط برای غیرفعال بودن
        return super().user_can_authenticate(user) and user.is_active