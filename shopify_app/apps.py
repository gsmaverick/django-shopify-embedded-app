import os

from django.apps import AppConfig


class ShopifyAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shopify_app"

    # Doc: https://shopify.dev/docs/apps/auth/oauth
    SHOPIFY_API_KEY = os.environ.get("SHOPIFY_CLIENT_ID")
    SHOPIFY_API_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")

    # Doc: https://shopify.dev/docs/api/usage/versioning
    SHOPIFY_API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "unstable")

    # Doc: https://shopify.dev/docs/api/usage/access-scopes
    SHOPIFY_API_SCOPES = os.environ.get(
        "SHOPIFY_API_SCOPES",
        "read_products,write_products",
    )

    APP_URL = os.environ.get("APP_URL")
