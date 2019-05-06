# Generated by Django 2.2 on 2019-05-05 13:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=5, verbose_name='姓名')),
                ('student_id', models.CharField(max_length=11, verbose_name='学号')),
                ('cloud_id', models.CharField(max_length=20, verbose_name='云顶号')),
                ('email', models.CharField(max_length=30, verbose_name='邮箱')),
                ('magor', models.CharField(choices=[('M', '机电创新团队'), ('P', 'Python'), ('N', 'Node.js'), ('J', 'Java'), ('F', '前端'), ('D', '设计')], max_length=1, verbose_name='方向')),
                ('grade', models.CharField(max_length=4, verbose_name='年级')),
                ('room', models.CharField(max_length=8, verbose_name='宿舍号')),
                ('home_address', models.CharField(max_length=100, verbose_name='家庭住址')),
                ('guardian_phone', models.CharField(max_length=11, verbose_name='家长手机号')),
                ('introduction', models.CharField(max_length=350, verbose_name='个人介绍')),
                ('involved_projects', models.TextField()),
                ('management_projects', models.TextField()),
                ('read_notifications', models.TextField()),
                ('unread_notifications', models.TextField()),
                ('sex', models.CharField(choices=[('m', '男'), ('f', '女')], max_length=1, verbose_name='性别')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
