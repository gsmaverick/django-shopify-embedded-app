from django.apps import apps
from django import urls
import shopify

from shopify_app import models


def create_or_update_shop(shop_domain, access_token, access_scopes):
    shop, created = models.Shop.objects.get_or_create(shopify_domain=shop_domain)
    shop.shopify_access_token = access_token
    shop.access_scopes = access_scopes
    shop.save()

    return shop, created


def after_authenticate_jobs(shop):
    webhook = shopify.Webhook()
    webhook.topic = "app/uninstalled"
    webhook.address = "http://{app_url}{uninstall_path}".format(
        app_url=apps.get_app_config("shopify_app").APP_URL,
        uninstall_path=urls.reverse("shopify_webhooks_shop_uninstall"),
    )
    webhook.format = "json"
    webhook.save()
