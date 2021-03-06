# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-04 21:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_dir_url', models.CharField(max_length=500)),
                ('agent_name', models.CharField(max_length=30)),
                ('agent_version', models.IntegerField()),
                ('agent_repository_url', models.CharField(max_length=500)),
                ('agent_date', models.DateTimeField(verbose_name='date downloaded')),
                ('agent_json_data', models.TextField()),
                ('agent_state', models.IntegerField(choices=[(0, 'success'), (1, 'in-progress'), (2, 'permanent fail'), (3, 'duplicate')], default=1)),
                ('agent_md5hash', models.CharField(max_length=36)),
                ('pdf2txt_version', models.IntegerField(null=True)),
                ('pdf2txt_state', models.IntegerField(choices=[(0, 'success'), (1, 'in-progress'), (2, 'permanent fail'), (3, 'duplicate')], default=1)),
                ('pdf2txt_date', models.DateTimeField(null=True, verbose_name='date converted')),
                ('pdf2txt_md5hash', models.CharField(max_length=36)),
                ('cleantxt_version', models.IntegerField(null=True)),
                ('cleantxt_state', models.IntegerField(choices=[(0, 'success'), (1, 'in-progress'), (2, 'permanent fail'), (3, 'duplicate')], default=1)),
                ('cleantxt_date', models.DateTimeField(null=True, verbose_name='date cleaned')),
                ('cleantxt_md5hash', models.CharField(max_length=36)),
                ('index_version', models.IntegerField(null=True)),
                ('index_state', models.IntegerField(choices=[(0, 'success'), (1, 'in-progress'), (2, 'permanent fail'), (3, 'duplicate')], default=1)),
                ('index_date', models.DateTimeField(null=True, verbose_name='date cleaned')),
                ('agent_dup', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='agentdup', to='document.Document')),
                ('pdf2txt_dup', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='pdfdup', to='document.Document')),
            ],
        ),
    ]
