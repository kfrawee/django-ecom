from functools import wraps
from django.contrib.auth.models import User


def bypass_user_auth_decorator(method):
    def bypass_user_auth(request):
        """For testing only, assume user0 is logged in"""
        if not request.user.is_authenticated:
            try:
                user = User.objects.get(username="user0")
                request.user = user
            except User.DoesNotExist:
                log_msg = "Please run `python manage.py seedusers` first"
                raise Exception(log_msg)

        return request

    @wraps(method)
    def wrapper(self, request, *args, **kwargs):
        request = bypass_user_auth(request)
        return method(self, request, *args, **kwargs)

    return wrapper
