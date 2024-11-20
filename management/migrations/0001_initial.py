# Generated by Django 4.2.7 on 2024-01-04 13:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Management",
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
                (
                    "management_name",
                    models.CharField(
                        blank=True,
                        default="N/A",
                        max_length=240,
                        null=True,
                        verbose_name="Dirección",
                    ),
                ),
                (
                    "management_in_charge",
                    models.CharField(
                        blank=True,
                        default="N/A",
                        max_length=240,
                        null=True,
                        verbose_name="Encargado",
                    ),
                ),
                (
                    "management_in_charge_mail",
                    models.CharField(
                        blank=True,
                        default="N/A",
                        max_length=240,
                        null=True,
                        verbose_name="Encargado Correo",
                    ),
                ),
                (
                    "state",
                    models.CharField(
                        blank=True,
                        default="Activo",
                        max_length=100,
                        null=True,
                        verbose_name="Estado",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha Creación"
                    ),
                ),
                (
                    "updated",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Fecha Actualización"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        default=0,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Direcciones",
                "verbose_name_plural": "Direccioness",
                "ordering": ["management_name"],
            },
        ),
    ]
