# Generated by Django 3.2.21 on 2023-09-21 06:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventree_kicad', '0003_selectedcategory_default_reference'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='selectedcategory',
            options={'verbose_name': 'KiCad Category', 'verbose_name_plural': 'KiCad Categories'},
        ),
    ]
