# Generated by Django 4.1.7 on 2023-10-07 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_alter_user_profile_img'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_img',
            field=models.ImageField(blank=True, null=True, upload_to='myapp/images'),
        ),
    ]
