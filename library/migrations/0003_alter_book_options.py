# Generated by Django 5.1.1 on 2024-10-23 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_category_librarysetting_student_book_borrowing'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'ordering': ['add_at']},
        ),
    ]
