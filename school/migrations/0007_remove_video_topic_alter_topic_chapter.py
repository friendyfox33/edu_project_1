# Generated by Django 4.2.5 on 2023-10-11 10:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0006_topic_chapter'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='video',
            name='topic',
        ),
        migrations.AlterField(
            model_name='topic',
            name='chapter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='school.chapter', verbose_name='Розділ'),
        ),
    ]
