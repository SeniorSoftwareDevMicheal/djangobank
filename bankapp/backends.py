from django.contrib.auth.backends import ModelBackend
from bankapp.models import MyUser

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = MyUser.objects.get(email=email)
        except MyUser.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
