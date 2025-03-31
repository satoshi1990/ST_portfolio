# Generated by Django 5.1.1 on 2025-03-28 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_folder', '0006_pokedex'),
    ]

    operations = [
        migrations.CreateModel(
            name='Common_ST',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=50, null=True, verbose_name='キー')),
                ('value', models.CharField(blank=True, max_length=50, null=True, verbose_name='値')),
            ],
            options={
                'verbose_name_plural': 'common_STPortfolio',
                'db_table': 'ST_common',
                'ordering': ['id'],
            },
        ),
    ]
