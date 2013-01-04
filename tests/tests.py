from django.test import TestCase
from models import Topic
from ct.manager import ClassManager, InstanceManager

class ModelTest(TestCase):
	fixtures = ['chapter.json',]

	def test_ctModel(self):
		"""
			We have to check about something like:
			
			CREATE TABLE "tests_topic_ct_index" (
    			"id" integer NOT NULL PRIMARY KEY,
    			"ancestor" integer NOT NULL,
    			"descendant" integer NOT NULL,
    			"path_length" integer unsigned NOT NULL,
    			
    			UNIQUE ("ancestor", "descendant")
			)
		"""
		# Check table name
		self.assertEqual(Topic.index._ctModel._meta.db_table, 'tests_topic_ct_index')

		# Check fields
		fieldSet = set(Topic.index._ctModel._meta.get_all_field_names())
		self.assertEqual(set(['id', 'ancestor', 'descendant', 'path_length']), fieldSet)

		# Check UNIQUE constrain
		uniqueSet = set(Topic.index._ctModel._meta.unique_together)
		self.assertEqual(set([('ancestor', 'descendant')]), uniqueSet)
			
	def test_classManager(self):
		self.assertTrue(isinstance(Topic.index, ClassManager))
		
	def test_instanceManager(self):
		a = Topic.objects.get(pk=1)
		self.assertTrue(isinstance(a.index, InstanceManager))

	def test_postSave(self):
		a = Topic(name='My special topic')
		a.save()
		# For each topic in the Topic model we need a self
		# referencing element in the closure table.
		topics = Topic.objects.all()
		for topic in topics:
			ct = Topic.index._ctModel.objects.get(ancestor=topic)
			self.assertTrue(ct.ancestor == ct.descendant and ct.path_length == 0)

	def test_topic(self):
		a = Topic.objects.get(pk=1)
		t = unicode(a)
		self.assertTrue(a.name in t)
		self.assertTrue('(%s)' % a.id in t)
