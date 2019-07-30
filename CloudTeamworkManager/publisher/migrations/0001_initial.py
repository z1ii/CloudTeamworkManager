# Generated by Django 2.2 on 2019-07-30 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='personal_comment',
            fields=[
                ('detail', models.TextField(verbose_name='内容')),
                ('id', models.CharField(max_length=15, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='personal_progress',
            fields=[
                ('detail', models.TextField(verbose_name='内容')),
                ('id', models.CharField(max_length=15, primary_key=True, serialize=False)),
            ],
            options={
                'permissions': {('edit_personal_progress', '编辑个人进度')},
            },
        ),
        migrations.CreateModel(
            name='personal_shedule',
            fields=[
                ('detail', models.TextField(verbose_name='内容')),
                ('id', models.CharField(max_length=15, primary_key=True, serialize=False)),
            ],
            options={
                'permissions': {('edit_personal_shedule', '编辑个人时间表')},
            },
        ),
    ]
