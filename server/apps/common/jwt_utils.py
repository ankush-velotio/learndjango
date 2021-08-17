import datetime
import jwt

from django.conf import settings
from rest_framework.exceptions import NotAuthenticated


def generate_jwt_access_token(user):
    # Create payload for JWT token
    payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2),
        'iat': datetime.datetime.utcnow()
    }

    # Create JWT access token
    access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')

    return access_token


def generate_jwt_refresh_token(user):
    # Create payload for JWT refresh token
    refresh_token_payload = {
        'id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=3),
        'iat': datetime.datetime.utcnow()
    }

    # Create JWT refresh token
    refresh_token = jwt.encode(refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256').decode('utf-8')

    return refresh_token


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
