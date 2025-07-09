from django.contrib.auth.backends import ModelBackend
from .models import User


class MobileBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        mobile = kwargs['mobile']
        try:
            user = User.objects.get(mobile=mobile)
            user.check_password(password)
            return user
        except User.DoesNotExist:
            pass
