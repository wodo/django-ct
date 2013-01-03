from django.db import models
from ct import models as ct

class Thing(models.Model):
    name = models.TextField()    
    book = ct.ClosureTable()

    def __unicode__(self):
        return u'(%s) %s' % (self.id, self.name)
        