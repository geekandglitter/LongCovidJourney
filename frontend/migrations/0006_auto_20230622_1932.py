# Generated by Django 3.2.13 on 2023-06-22 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0005_alter_allcontents_fullpost'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NEWAllContents',
        ),
        migrations.DeleteModel(
            name='NEWAllPosts',
        ),
        migrations.DeleteModel(
            name='NEWSearchTerms',
        ),
        migrations.RemoveField(
            model_name='allposts',
            name='postid',
        ),
        migrations.AddField(
            model_name='allposts',
            name='fullpost',
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
        migrations.AlterField(
            model_name='allcontents',
            name='fullpost',
            field=models.TextField(blank=True, max_length=5000, null=True),
        ),
    ]
