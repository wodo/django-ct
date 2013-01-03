from django.test import TestCase
from models import Thing
from ct.manager import ClassManager, InstanceManager

class ModelTest(TestCase):
	fixtures = ['chapter.json',]
	
	def test_ctModel(self):
		'''
			We have to check about something like:
			
			CREATE TABLE "tests_thing_ct_book" (
    			"id" integer NOT NULL PRIMARY KEY,
    			"ancestor" integer NOT NULL,
    			"descendant" integer NOT NULL,
    			"path_length" integer unsigned NOT NULL,
    			
    			UNIQUE ("ancestor", "descendant")
			)
		'''
		# Check table name
		self.assertEqual(Thing.book._ctModel._meta.db_table, 'tests_thing_ct_book')

		# Check fields
		fieldSet = set(Thing.book._ctModel._meta.get_all_field_names())
		self.assertEqual(set(['id', 'ancestor', 'descendant', 'path_length']), fieldSet)

		# Check UNIQUE constrain
		uniqueSet = set(Thing.book._ctModel._meta.unique_together)
		self.assertEqual(set([('ancestor', 'descendant')]), uniqueSet)
			
	def test_classManager(self):
		self.assertTrue(isinstance(Thing.book, ClassManager))
		
	def test_instanceManager(self):
		a = Thing.objects.get(pk=1)
		self.assertTrue(isinstance(a.book, InstanceManager))

	def test_postSave(self):
		# For each thing in the Thing model we need a self
		# referencing element in the closure table.
		things = Thing.objects.all()
		for thing in things:
			ct = Thing.book._ctModel.objects.get(ancestor=thing)
			self.assertTrue(ct.ancestor == ct.descendant and ct.path_length == 0)
