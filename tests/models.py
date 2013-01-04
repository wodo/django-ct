from django.db import models
from ct import models as ct

class Topic(models.Model):
    name = models.TextField()    
    index = ct.ClosureTable()

    def __unicode__(self):
        return u'(%s) %s' % (self.id, self.name)
