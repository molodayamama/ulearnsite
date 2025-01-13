# Generated by Django 5.1.4 on 2025-01-13 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='skill',
            options={'ordering': ['-count'], 'verbose_name': 'Навык', 'verbose_name_plural': 'Навыки'},
        ),
        migrations.AddField(
            model_name='skill',
            name='is_general',
            field=models.BooleanField(default=True, verbose_name='Общая статистика'),
        ),
    ]
