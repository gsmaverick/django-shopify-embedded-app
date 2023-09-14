from django.urls import path

from . import views

urlpatterns = [
    # Embedded app and OAuth flow views
    path("embedded_app/", views.embedded_app, name="shopify_embedded_app"),
    path(
        "embedded_app/callback/",
        views.embedded_app_callback,
        name="shopify_embedded_app_callback",
    ),
    # Mandatory Shopify App Webhooks
    path(
        "webhooks/customers/data_redact/",
        views.webhooks_customers_data_redact,
        name="shopify_webhooks_customers_data_redact",
    ),
    path(
        "webhooks/customers/data_request/",
        views.webhooks_customers_data_request,
        name="shopify_webhooks_customers_data_request",
    ),
    path(
        "webhooks/shop/redact/",
        views.webhooks_shop_redact,
        name="shopify_webhooks_shop_redact",
    ),
    path(
        "webhooks/shop/uninstall/",
        views.webhooks_shop_uninstall,
        name="shopify_webhooks_shop_uninstall",
    ),
    # APIs requiring Shopify Session Token
    path(
        "api/products/",
        views.api_products,
        name="shopify_api_products",
    ),
]
