# Generated by Django 5.1.4 on 2024-12-26 20:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("theatre", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="reservation",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="performance",
            name="theatre_hall",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="theatre.theatrehall"
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="performance",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="theatre.performance",
            ),
        ),
        migrations.AddField(
            model_name="ticket",
            name="reservation",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tickets",
                to="theatre.reservation",
            ),
        ),
        migrations.AddConstraint(
            model_name="ticket",
            constraint=models.UniqueConstraint(
                fields=("performance", "row", "seat"),
                name="unique_ticket_performance_row_seat",
            ),
        ),
    ]
