# Generated by Django 4.2.17 on 2024-12-15 11:12

import base.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("competition", "0002_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="series",
            options={
                "ordering": ["semester", "order"],
                "verbose_name": "séria",
                "verbose_name_plural": "série",
            },
        ),
        migrations.AlterField(
            model_name="publication",
            name="file",
            field=base.models.RestrictedFileField(
                blank=True, upload_to="publications/%Y/", verbose_name="súbor"
            ),
        ),
    ]