import datetime
import time

import jwt
import logging

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import NotAuthenticated
from rest_framework_jwt.serializers import jwt_decode_handler
from rest_framework_jwt.settings import api_settings

from common.messages import NOT_AUTHENTICATED_ERROR, SIGNATURE_EXPIRED_ERROR

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def generate_jwt_access_token(user):
    # Create payload for JWT token
    payload = jwt_payload_handler(user)

    # Create JWT access token
    access_token = jwt_encode_handler(payload)

    return access_token


def generate_jwt_refresh_token(user):
    # Create payload for JWT refresh token
    refresh_token_payload = {
        "id": user.id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=3),
        "iat": datetime.datetime.utcnow(),
    }

    # Create JWT refresh token
    refresh_token = jwt.encode(
        refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm="HS256"
    ).decode("utf-8")

    return refresh_token


def verify_jwt_token(token):
    if not token:
        raise NotAuthenticated(NOT_AUTHENTICATED_ERROR)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise NotAuthenticated(SIGNATURE_EXPIRED_ERROR)

    return payload


def verify_jwt_refresh_token(refresh_token):
    if not refresh_token:
        raise NotAuthenticated(NOT_AUTHENTICATED_ERROR)
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        raise NotAuthenticated(SIGNATURE_EXPIRED_ERROR)

    return payload


def blacklist_jwt_token(token):
    try:
        payload = jwt_decode_handler(token)
        key = f"JWT {token}"
        ttl = payload.get("exp") - int(time.time())

        if ttl > 0:
            cache.set(key, "", timeout=ttl)
            return True

        logging.info("Token is expired.")
        return False
    except Exception as e:
        raise e
