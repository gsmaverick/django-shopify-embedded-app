from django.contrib import admin

from .models import Shop


class ShopAdmin(admin.ModelAdmin):
    exclude = ["shopify_access_token"]

    readonly_fields = [
        "created_at",
        "updated_at",
        "shopify_domain",
        "shopify_access_token",
        "access_scopes",
    ]


admin.site.register(Shop, ShopAdmin)
