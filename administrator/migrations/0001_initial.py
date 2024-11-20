# Generated by Django 4.2.7 on 2023-12-27 21:28

import administrator.models
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Config",
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
                    "app_name",
                    models.CharField(
                        blank=True,
                        max_length=240,
                        null=True,
                        verbose_name="Nombre Municipalidad",
                    ),
                ),
                (
                    "app_type",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Tipo Flujo"
                    ),
                ),
                ("logo_path", models.ImageField(upload_to=administrator.models.logo)),
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
            ],
            options={
                "verbose_name": "Configuración",
                "verbose_name_plural": "Configuraciones",
                "ordering": ["app_name"],
            },
        ),
    ]
