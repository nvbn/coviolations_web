# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Task'
        db.delete_table(u'tasks_task')

        # Deleting model 'Violation'
        db.delete_table(u'tasks_violation')


    def backwards(self, orm):
        # Adding model 'Task'
        db.create_table(u'tasks_task', (
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['projects.Project'], null=True, blank=True)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('commit', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tasks', ['Task'])

        # Adding model 'Violation'
        db.create_table(u'tasks_violation', (
            ('status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='violations', to=orm['tasks.Task'])),
            ('prepared_data', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('violation', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('raw_data', self.gf('django.db.models.fields.TextField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'tasks', ['Violation'])


    models = {
        
    }

    complete_apps = ['tasks']