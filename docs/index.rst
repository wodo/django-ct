.. dango-ct documentation master file, created by
   sphinx-quickstart on Sat Dec  1 13:26:10 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to dango-ct's documentation!
====================================

Contents:

.. toctree::
   :maxdepth: 2
   
Some Research
=============

* `Managing hierarchies`__ in SQL
* What is the most efficient/elegant way to `parse a flat table into a tree`__?
* The simplest(?) way to do `tree-based queries`__ in SQL
* Rendering Trees with `Closure Tables`__
* The Term TCT (`transitive closure tables`__)
* `Hierarchical Data`__: Persistence via Closure Table
* The `Slides`__ of Bill Karwin
* A `gist`__ with a PHP implementation.
* Optimize `Hierarchy Queries`__ with a Transitive Closure Table
* `Hierarchy Queries`__ - Creating a Transitive Closure to Optimize Rollups (Steven F. Lott)
* `Moving Subtrees in Closure Table Hierarchies`__
* Bill Karwin: `SQL Antipatterns`__: Avoiding the Pitfalls of Database Programming

__ http://www.mysqlperformanceblog.com/2011/02/14/moving-subtrees-in-closure-table/
__ http://stackoverflow.com/questions/8196175/managing-hierarchies-in-sql-mptt-nested-sets-vs-adjacency-lists-vs-storing-path
__ http://stackoverflow.com/questions/192220/what-is-the-most-efficient-elegant-way-to-parse-a-flat-table-into-a-tree/192462#192462
__ http://dirtsimple.org/2010/11/simplest-way-to-do-tree-based-queries.html
__ http://karwin.blogspot.de/2010/03/rendering-trees-with-closure-tables.html
__ http://www.phpclasses.org/package/5479-PHP-Manage-transitive-closure-tables-stored-in-MySQL.html
__ http://b2berry.com/2011/11/19/hierarchical-data-persistence-via-closure-table/
__ http://www.slideshare.net/billkarwin/models-for-hierarchical-data
__ http://gist.github.com/1380975
__ http://kylecordes.com/2008/transitive-closure
__ http://www.itmaybeahack.com/homepage/_static/transclose/transclose.html
__ http://www.pragprog.com/titles/bksqla/sql-antipatterns

Test Data Sources
=================

* Integrated Taxonomic Information System (ITIS_)

.. _ITIS: http://www.itis.gov

Requirements
============

* Every class "C" is associated with one ore more closure table classes "C.CTn"
* There is a possibility to manage more the one tree "T" inside of one closure table "C.CTn".
* | Every new instance "I" of "C" will be automatically added to its associated closure tables "C.CTn"
  | (Building a tree "T" with one node. The root node)
* An instance "I" of "C" always has at least one reference in its closure table "C.CTn". 
* | When a instance "I" of "C" is deleted, all references to "I" in "C.CTn" are be deleted too.
  | (The tree structure is preserved)
* We need a ability to connect a tree "T" with a subtree "ST".
* | We need a ability to isolate a subtree "ST" from its tree "T".
  | (This generates a new tree)

SQL Snippets
============

A closure table is a way of storing hierarchies.
It involves storing all path through the tree,
not just those with a direct parent-child realtionship [1]_.

:: 

  ct(c)

  CREATE TABLE ct (
      ancestor INTEGER NOT NULL REFERENCES c (id) ON DELETE CASCADE,
      descendant INTEGER NOT NULL REFERENCES c (id)  ON DELETE CASCADE,
      length INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (ancestor, descendant)
  )

To create a new node, we first insert the self referencing row [2]_.

:: 

  create(t)
  
  INSERT INTO ct (ancestor, descendant) VALUES (t,t)

We need to insert all the nodes of the new subtree.
We use a Cartesian join between the ancestors of "st" (going up)
and the descendants of "t" (going down) [3]_.

::

  connect(t, st)

  INSERT INTO ct (ancestor, descendant, length)
  SELECT supertree.ancestor, subtree.descendant, supertree.length+subtree.length+1
  FROM ct AS supertree JOIN ct AS subtree
  WHERE subtree.ancestor = t
  AND supertree.descendant = st

To move a subtree from one location in the tree to another,
first disconnect the subtree from its ancestors by deleting rows that reference
the ancestors of the top node in the subtree and the descendants of that node.
Make sure not to delete the self referencing row of "st".
By selecting the ancestors of "st", but not "st" itself, and descendants of "st",
including "st", this correctly removes all the paths from "st"'s ancestors
to "st" and its descendants [4]_.

::

  disconnect(st)
  
  DELETE FROM ct
  WHERE descendant IN (SELECT descendant
                       FROM ct
                       WHERE ancestor = st)
  AND ancestor NOT IN (SELECT descendant
                       FROM ct
                       WHERE ancestor = st
                       AND ancestor != descendant)

.. [1] Bill Karwin: `SQL Antipatterns`_: Avoiding the Pitfalls of Database Programming - Page 36
.. [2] Bill Karwin: `SQL Antipatterns`_: Avoiding the Pitfalls of Database Programming - Page 38
.. [3] Bill Karwin: `Moving Subtrees in Closure Table Hierarchies`__
.. [4] Bill Karwin: `SQL Antipatterns`_: Avoiding the Pitfalls of Database Programming - Page 39
__ http://www.mysqlperformanceblog.com/2011/02/14/moving-subtrees-in-closure-table/
.. _`SQL Antipatterns`: http://www.pragprog.com/titles/bksqla/sql-antipatterns

Many thanks to Bill Karwin for these beautiful "how to implements a closure table" ideas.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
