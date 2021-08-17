import jwt

from django.conf import settings
from rest_framework.exceptions import NotAuthenticated


def verify_jwt_token(token):
    if not token:
        raise NotAuthenticated('Unauthenticated!')
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise NotAuthenticated('Authentication failed! Signature Expired!')

    return payload


def verify_jwt_refresh_token(refresh_token):
    if not refresh_token:
        raise NotAuthenticated('Unauthenticated!')
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise NotAuthenticated('Authentication failed! Signature Expired!')

    return payload
