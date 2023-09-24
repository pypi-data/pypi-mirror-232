# Generated by Django 2.2.12 on 2020-04-25 09:42

import byro.public.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("public", "0002_memberpageprofile_publication_consent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="memberpageprofile",
            name="secret_token",
            field=models.CharField(
                blank=True,
                default=byro.public.models.generate_default_token,
                max_length=128,
                null=True,
                unique=True,
            ),
        ),
    ]
