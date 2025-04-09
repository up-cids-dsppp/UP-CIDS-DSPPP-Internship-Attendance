from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Intern
from django.contrib.auth.models import AnonymousUser

class InternJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization').split()[1])
            email = validated_token.get('email')
            user_type = validated_token.get('user_type')

            if user_type == 'intern':
                try:
                    intern = Intern.objects.get(email=email)
                    return (intern, validated_token)
                except Intern.DoesNotExist:
                    return None
        except Exception:
            return None

        return None