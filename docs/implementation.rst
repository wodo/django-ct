.. _imp_details:

Implementation Details
======================

.. note:: The book "Pro Django" from Marty Alchin is a great source of knowledge.
    I took a lot of ideas from it. For me realizing an application like django-ct
    is not possible without the knowledge out of this book.

This section provides an overview of the features that will be available when
the application is completed, so we can start seeing these features fall into
place as the code progresses.

First the act of assigning a manager to the model that need the possibilities
of a closure table. This should be as simple as possible, preferably just a single
attribute assignment. Simply pick a name and assign an object, just like Django's
own model fields.

.. literalinclude:: ../tests/models.py
    :language: python
    :emphasize-lines: 2,6

That's enough to get everything configured. From there, the framework is able to set up
a model behind the scenes to store the closure table entries and the ``index`` attribute
can be used to access those information using the API methods of django-ct.

The whole registration of the manager begins by assigning a ``ClosureTable`` object to
a model, so that's a good place to start defining code. There are a number of things that
have to happen in sequence to get the closure table system initialized for a particular
model; at a high level ``ClosureTable`` manages the following tasks:

* Create a model for the requested closure table in a way that the foreign keys
  from this table referencing the related objects in the original
  model (``create_model()``).
* Register signal handlers to execute when the original model is saved.
  These in turn add new rows to the closure table each time a new instance of the model
  is saved.
* Assign a descriptor to the original model, using the attribute name where the
  ``ClosureTable`` was assigned. This descriptor will forward the work to a
  ``InstanceManager`` object or a ``ClassManager`` object.
  
Before any of those steps can really begin, there's a small amount of housekeeping
that must be done. Since the ``ClosureTable`` object gets assigned as an attribute of
a model, the first chance it gets to execute is in the ``contribute_to_class()`` method.

.. literalinclude:: ../ct/models.py
    :language: python
    :pyobject: ClosureTable.contribute_to_class

So far is's not much, but this is the only point in the process where Django tells
``ClosureTable`` what name it was given when assigned to the model. This is stored away
for future reference. The method ``contribute_to_class()`` gets called on each
field in turn, in the order they appear in the namespace dictionary Python created for
the model's definition. Since standard dictionaries don't have a guaranteed order,
there's no way to predict how many fields will already have been processed by the time
``ClosureTable`` gets a chance to peek at the model.

To solve this, we turn to a signal: ``class_prepared``. Django fires this signal once
all the fields and managers have been added to the model and everything is in place
to be used by external code. That's when ``ClosureTable`` will have guaranteed access
to the model so ``contribute_to_class()`` continuous by setting up a listener
for ``class_prepared``.

Django will now call ``ClosureTable.finalize()`` with the fully-prepared model once
everything is in place to continue processing it. That method is the responsible for
performing all of the remaining tasks. Most of the details are delegated to other
methods, but ``finalize()`` coordinates them.

.. literalinclude:: ../ct/models.py
    :language: python
    :pyobject: ClosureTable.finalize
    
There are a few different sub-steps required in creating a closure table. Adding all
the logic in one method would hamper readability and maintainability, so it's been
broken up into three additional methods (``create_model()``, ``get_fields()`` and
``get_options()``).

.. literalinclude:: ../ct/models.py
    :language: python
    :pyobject: ClosureTable.create_model
    
Django is Python! So we use here all the hard core Python stuff to create a
new Django model class. The ``create_model()`` method above mimic the process of creating
a model like in this code:

.. code-block:: python

    from django.db import models
    from tests.models import Topic
    
    class Topic_ct_index(models.Model):
        ancestor = models.ForeignKey(Topic, related_name='+', on_delete=models.CASCADE,
                                     blank=False, null=False)
        descendant = models.ForeignKey(Topic, related_name='+', on_delete=models.CASCADE,
                                       blank=False, null=False),
        path_length = models.PositiveIntegerField(default=0, blank=False, null=False)
        
        class Meta:
            unique_together = ('ancestor', 'descendant')

On this way we implement a model inside the database that looks like
the original proposal from `Bill Karwin`__:

__ http://karwin.blogspot.de/2010/03/rendering-trees-with-closure-tables.html

.. code-block:: sql

  ct(c)

  CREATE TABLE ct (
      ancestor INTEGER NOT NULL REFERENCES c (id) ON DELETE CASCADE,
      descendant INTEGER NOT NULL REFERENCES c (id)  ON DELETE CASCADE,
      length INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (ancestor, descendant)
  )

The last two lines of the methode ``finalize()`` assignes a so called descriptor 
to the original model. This results in an for example ``index`` attribute
in the model ``Topic``. This attribute is implemented as a ``Descriptor`` object.

.. literalinclude:: ../ct/manager.py
    :language: python
    :pyobject: Descriptor

With this django-ct can provide two different kind of API's. If we use the ``index``
like a class property the API will be provided by a ``ClassManager``. If we use the ``index``
attribute like a instance property the API will be provided by a ``InstanceManager``.

.. code::

    $ python manage.py shell
    >>> from tests.models import Topic
    >>> type(Topic.index)
    <class 'ct.manager.ClassManager'>
    >>> a = Topic.objects.get(pk=1)
    >>> type(a.index)
    <class 'ct.manager.InstanceManager'>
    >>> exit()
