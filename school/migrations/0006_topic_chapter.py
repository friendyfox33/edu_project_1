# Generated by Django 4.2.5 on 2023-10-11 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0005_alter_topicvideo_options_delete_chaptertopic'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='chapter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='school.chapter', verbose_name='Наукова дисципліна'),
            preserve_default=False,
        ),
    ]
