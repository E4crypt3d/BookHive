# Generated by Django 5.1.1 on 2024-10-30 13:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_borrowing_unique_active_borrowing'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='borrowing',
            options={'ordering': ['add_at']},
        ),
    ]
