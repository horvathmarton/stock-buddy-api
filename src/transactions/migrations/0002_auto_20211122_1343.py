# Generated by Django 3.2.8 on 2021-11-22 13:43

# pylint: disable=missing-module-docstring, invalid-name, missing-class-docstring

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("stocks", "0002_auto_20211122_1207"),
        ("transactions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cashtransaction",
            name="portfolio",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.RESTRICT,
                to="stocks.stockportfolio",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="forextransaction",
            name="portfolio",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.RESTRICT,
                to="stocks.stockportfolio",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="stocktransaction",
            name="portfolio",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.RESTRICT,
                to="stocks.stockportfolio",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="stocktransaction",
            name="comment",
            field=models.TextField(null=True),
        ),
    ]
