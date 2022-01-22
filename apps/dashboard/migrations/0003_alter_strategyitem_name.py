# Generated by Django 3.2.8 on 2022-01-22 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_userstrategy"),
    ]

    operations = [
        migrations.AlterField(
            model_name="strategyitem",
            name="name",
            field=models.CharField(
                choices=[
                    ("stock", "Stock"),
                    ("bond", "Bond"),
                    ("real-estate", "Real Estate"),
                    ("crypto", "Crypto"),
                    ("gold", "Gold"),
                    ("commodity", "Commodity"),
                    ("cash", "Cash"),
                ],
                max_length=11,
            ),
        ),
    ]
