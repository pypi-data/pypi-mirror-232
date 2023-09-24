# Generated by Django 2.1.7 on 2019-02-26 21:38

import byro.public.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("public", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="memberpageprofile",
            name="publication_consent",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                blank=True, default=byro.public.models.get_default_consent, null=True
            ),
        )
    ]
