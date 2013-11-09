# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LastFmUser'
        db.create_table('lastgui_lastfmuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('requested_update', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('last_check', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('external_until', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('fetching', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('lastgui', ['LastFmUser'])

        # Adding model 'Poster'
        db.create_table('lastgui_poster', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='posters', to=orm['lastgui.LastFmUser'])),
            ('start', self.gf('django.db.models.fields.DateField')()),
            ('end', self.gf('django.db.models.fields.DateField')()),
            ('params', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('requested', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('completed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('failed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('expires', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('error', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('node', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lastgui.Node'], null=True, blank=True)),
            ('pdf_url', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('svg_url', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('lastgui', ['Poster'])

        # Adding model 'Node'
        db.create_table('lastgui_node', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('nodename', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('salt', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('disabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('lastseen', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('lastgui', ['Node'])


    def backwards(self, orm):
        # Deleting model 'LastFmUser'
        db.delete_table('lastgui_lastfmuser')

        # Deleting model 'Poster'
        db.delete_table('lastgui_poster')

        # Deleting model 'Node'
        db.delete_table('lastgui_node')


    models = {
        'lastgui.lastfmuser': {
            'Meta': {'object_name': 'LastFmUser'},
            'external_until': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fetching': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_check': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'requested_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'lastgui.node': {
            'Meta': {'object_name': 'Node'},
            'disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastseen': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'nodename': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'lastgui.poster': {
            'Meta': {'object_name': 'Poster'},
            'completed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end': ('django.db.models.fields.DateField', [], {}),
            'error': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'expires': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'failed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'node': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lastgui.Node']", 'null': 'True', 'blank': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'pdf_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'requested': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateField', [], {}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'svg_url': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'posters'", 'to': "orm['lastgui.LastFmUser']"})
        }
    }

    complete_apps = ['lastgui']