# Generated by Django 4.2.5 on 2023-10-12 07:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0008_alter_video_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='sort_order_main',
            field=models.IntegerField(blank=True, help_text='Розраховується автоматично', null=True, verbose_name='Порядок виводу'),
        ),
    ]
