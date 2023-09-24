# Generated by Django 1.11.4 on 2017-08-12 11:03

import byro.common.models.auditable
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [("members", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "account_category",
                    models.CharField(
                        choices=[
                            ("member_donation", "member_donation"),
                            ("member_fees", "member_fees"),
                        ],
                        max_length=15,
                    ),
                ),
                ("name", models.CharField(max_length=300)),
                (
                    "member",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="members.Member",
                    ),
                ),
            ],
            bases=(byro.common.models.auditable.Auditable, models.Model),
        ),
        migrations.CreateModel(
            name="RealTransaction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "channel",
                    models.CharField(
                        choices=[("bank", "bank"), ("cash", "cash")], max_length=4
                    ),
                ),
                ("booking_datetime", models.DateTimeField(null=True)),
                ("value_datetime", models.DateTimeField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("purpose", models.CharField(max_length=200)),
                ("originator", models.CharField(max_length=200)),
                ("importer", models.CharField(max_length=200, null=True)),
                ("data", django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                (
                    "reverses",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="bookkeeping.RealTransaction",
                    ),
                ),
            ],
            bases=(byro.common.models.auditable.Auditable, models.Model),
        ),
        migrations.CreateModel(
            name="VirtualTransaction",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("value_datetime", models.DateTimeField(null=True)),
                (
                    "destination_account",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="incoming_transactions",
                        to="bookkeeping.Account",
                    ),
                ),
                (
                    "real_transaction",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="virtual_transactions",
                        to="bookkeeping.RealTransaction",
                    ),
                ),
                (
                    "source_account",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="outgoing_transactions",
                        to="bookkeeping.Account",
                    ),
                ),
            ],
            bases=(byro.common.models.auditable.Auditable, models.Model),
        ),
    ]
