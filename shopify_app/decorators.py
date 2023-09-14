import base64
from django.apps import apps
from django.http import HttpResponse, HttpResponseBadRequest
import hashlib
import hmac
import shopify
from shopify import session_token

from shopify_app import models


HTTP_AUTHORIZATION_HEADER = "HTTP_AUTHORIZATION"
SHOPIFY_HMAC_HEADER = "HTTP_X_SHOPIFY_HMAC_SHA256"


def session_token_required(func):
    def wrapper(*args, **kwargs):
        try:
            decoded_session_token = session_token.decode_from_header(
                authorization_header=args[0].META.get(HTTP_AUTHORIZATION_HEADER),
                api_key=apps.get_app_config("shopify_app").SHOPIFY_API_KEY,
                secret=apps.get_app_config("shopify_app").SHOPIFY_API_SECRET,
            )
            with _shopify_session(decoded_session_token):
                return func(*args, **kwargs)
        except session_token.SessionTokenError:
            return HttpResponse(status=401)

    return wrapper


def verified_webhook(func):
    def wrapper(*args, **kwargs):
        digest = hmac.new(
            apps.get_app_config("shopify_app").SHOPIFY_API_SECRET.encode("utf-8"),
            args[0].body,
            digestmod=hashlib.sha256,
        ).digest()
        computed_hmac = base64.b64encode(digest)

        if hmac.compare_digest(
            computed_hmac, args[0].META.get(SHOPIFY_HMAC_HEADER).encode("utf-8")
        ):
            return func(*args, **kwargs)
        else:
            return HttpResponseBadRequest(
                "Failed to verify webhook originated from Shopify"
            )

    return wrapper


def _shopify_session(session_token):
    shopify_domain = session_token.get("dest").removeprefix("https://")
    api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
    access_token = models.Shop.objects.get(
        shopify_domain=shopify_domain
    ).shopify_access_token

    return shopify.Session.temp(shopify_domain, api_version, access_token)
