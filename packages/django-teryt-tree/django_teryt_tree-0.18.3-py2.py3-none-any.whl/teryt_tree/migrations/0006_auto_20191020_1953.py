# Generated by Django 1.11 on 2019-10-21 00:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("teryt_tree", "0005_auto_20191020_1938"),
    ]

    operations = [
        migrations.AlterField(
            model_name="jednostkaadministracyjna",
            name="level",
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name="jednostkaadministracyjna",
            name="lft",
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
        migrations.AlterField(
            model_name="jednostkaadministracyjna",
            name="rght",
            field=models.PositiveIntegerField(db_index=True, editable=False),
        ),
    ]
