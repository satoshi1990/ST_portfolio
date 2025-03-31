# Generated by Django 5.1.1 on 2025-03-28 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_folder', '0005_remove_card_detail_card_summary_card_detail_all_card'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pokedex',
            fields=[
                ('pokedex_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='全国ポケモン図鑑ID')),
                ('name_j', models.CharField(max_length=50, null=True, verbose_name='ポケモン名_日本語')),
                ('name_e', models.CharField(blank=True, max_length=50, null=True, verbose_name='ポケモン名_英語')),
            ],
            options={
                'verbose_name_plural': 'pokedex',
                'db_table': 'app1_pokedex',
                'ordering': ['pokedex_id'],
            },
        ),
    ]
