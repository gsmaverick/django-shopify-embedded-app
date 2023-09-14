from django.db import models


class Shop(models.Model):
    # Base model traits
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shopify OAuth fields
    shopify_domain = models.CharField(max_length=255)
    shopify_access_token = models.CharField(max_length=255)
    access_scopes = models.TextField()
