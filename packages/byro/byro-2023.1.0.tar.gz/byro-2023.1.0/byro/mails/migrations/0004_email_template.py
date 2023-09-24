# Generated by Django 2.1.1 on 2018-09-11 19:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("mails", "0003_mailtemplate_reply_to")]

    operations = [
        migrations.AddField(
            model_name="email",
            name="template",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="mails.MailTemplate",
            ),
        )
    ]
