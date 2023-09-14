import binascii
from django import http, shortcuts, urls
from django.apps import apps
from django.views.decorators import clickjacking, csrf
import json
import logging
import os
import shopify
from shopify.utils import shop_url

from shopify_app import decorators, models
from .services import shop as shop_service

logger = logging.getLogger(__name__)

CSP_HEADER_VALUE = (
    lambda shop_domain: "frame-ancestors https://{} https://admin.shopify.com".format(
        shop_domain
    )
)


@clickjacking.xframe_options_exempt
def embedded_app(request):
    unsanitized_updated_access_scopes_required = request.GET.get(
        "updated_access_scopes_required"
    )
    unsanitized_is_embedded = request.GET.get("embedded")
    unsanitized_shop = request.GET.get("shop")

    sanitized_updated_access_scopes_required = (
        unsanitized_updated_access_scopes_required == "1"
    )
    sanitized_is_embedded = unsanitized_is_embedded == "1"
    sanitized_shop_domain = shop_url.sanitize_shop_domain(unsanitized_shop)

    if not sanitized_shop_domain:
        return http.HttpResponseBadRequest(
            "Shop must match 'example.myshopify.com' format"
        )

    app_installed = models.Shop.objects.filter(
        shopify_domain=sanitized_shop_domain
    ).exists()

    api_scopes = apps.get_app_config("shopify_app").SHOPIFY_API_SCOPES

    # Our app is not installed for this shop or updated access scopes are required.
    if not app_installed or sanitized_updated_access_scopes_required:
        redirect_uri = "http://{app_url}{callback_path}".format(
            app_url=apps.get_app_config("shopify_app").APP_URL,
            callback_path=urls.reverse("shopify_embedded_app_callback"),
        )

        state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
        request.session["shopify_oauth_state_param"] = state

        session = _get_shopify_session(sanitized_shop_domain)
        permission_url = session.create_permission_url(
            api_scopes.split(","), redirect_uri, state
        )

        return shortcuts.redirect(permission_url)

    # Our app is installed for this shop.
    shop = models.Shop.objects.get(shopify_domain=sanitized_shop_domain)

    # Our app only runs in embedded mode, if we're not running in embedded mode then
    # redirect to our app in Shopify admin.
    if not sanitized_is_embedded:
        return shortcuts.redirect(_embedded_app_in_shopify_admin_url(shop))

    # Our app is installed and running in embedded mode.
    scope_changes_required = shopify.ApiAccess(api_scopes) != shopify.ApiAccess(
        shop.access_scopes
    )
    response = shortcuts.render(
        request,
        "shopify_app/embedded_app.html",
        {
            "app_configuration": json.dumps(
                {
                    "shopDomain": sanitized_shop_domain,
                    "apiKey": apps.get_app_config("shopify_app").SHOPIFY_API_KEY,
                    "scopeChangesRequired": scope_changes_required,
                }
            ),
            "scope_changes_required": scope_changes_required,
        },
    )
    response["Content-Security-Policy"] = CSP_HEADER_VALUE(sanitized_shop_domain)
    return response


def embedded_app_callback(request):
    unsanitized_params = request.GET.dict()

    shopify.Session.setup(
        api_key=apps.get_app_config("shopify_app").SHOPIFY_API_KEY,
        secret=apps.get_app_config("shopify_app").SHOPIFY_API_SECRET,
    )

    if not shopify.Session.validate_params(unsanitized_params):
        return http.HttpResponseBadRequest(
            "Could not validate Shopify callback parameters"
        )

    sanitized_shop_domain = shop_url.sanitize_shop_domain(
        unsanitized_params.get("shop")
    )

    if not sanitized_shop_domain:
        return http.HttpResponseBadRequest(
            "Shop must match 'example.myshopify.com' format"
        )

    unsanitized_state = request.GET.get("state", "")
    if unsanitized_state != request.session["shopify_oauth_state_param"]:
        return HttpResponseForbidden("Could not verify OAuth state")

    api_version = apps.get_app_config("shopify_app").SHOPIFY_API_VERSION
    session = shopify.Session(sanitized_shop_domain, api_version)
    access_token = session.request_token(request.GET)

    shop, _ = shop_service.create_or_update_shop(
        sanitized_shop_domain,
        access_token,
        session.access_scopes,
    )

    with shopify.Session.temp(
        sanitized_shop_domain,
        api_version,
        shop.shopify_access_token,
    ):
        shop_service.after_authenticate_jobs(shop)

    return shortcuts.redirect(_embedded_app_in_shopify_admin_url(shop))


@csrf.csrf_exempt
@decorators.verified_webhook
def webhooks_customers_data_redact(request):
    return http.HttpResponse(status=501)


@csrf.csrf_exempt
@decorators.verified_webhook
def webhooks_customers_data_request(request):
    return http.HttpResponse(status=501)


@csrf.csrf_exempt
@decorators.verified_webhook
def webhooks_shop_redact(request):
    return http.HttpResponse(status=501)


@csrf.csrf_exempt
@decorators.verified_webhook
def webhooks_shop_uninstall(request):
    return http.HttpResponse(status=501)


@decorators.session_token_required
def api_products(request):
    products = shopify.Product.find()

    return http.JsonResponse(
        [
            {
                "id": product.id,
                "title": product.title,
            }
            for product in products
        ],
        safe=False,
    )


def _get_shopify_session(shop_url):
    shopify.Session.setup(
        api_key=apps.get_app_config("shopify_app").SHOPIFY_API_KEY,
        secret=apps.get_app_config("shopify_app").SHOPIFY_API_SECRET,
    )
    return shopify.Session(
        shop_url=shop_url,
        version=apps.get_app_config("shopify_app").SHOPIFY_API_VERSION,
    )


def _embedded_app_in_shopify_admin_url(shop):
    return (
        "https://admin.shopify.com/store/{shopify_store_domain}/apps/{api_key}".format(
            shopify_store_domain=shop.shopify_domain.split(".")[0],
            api_key=apps.get_app_config("shopify_app").SHOPIFY_API_KEY,
        )
    )
