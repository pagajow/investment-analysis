# Generated by Django 5.1.1 on 2025-04-07 17:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CookieConsentLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip_address", models.GenericIPAddressField()),
                ("user_agent", models.TextField()),
                (
                    "accepted_groups",
                    models.JSONField(
                        help_text="List of accepted cookie groups (e.g., ['essential', 'analytics'])"
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "policy_version",
                    models.CharField(
                        default="1.0",
                        help_text="Version of the privacy or cookie policy",
                        max_length=20,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        help_text="Logged-in user, if available.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
