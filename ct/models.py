from django.db import models
from ct.manager import Descriptor

__all__ = ['ClosureTable',]

class ClosureTable(object):

    def __init__(self):
        self.descriptor = Descriptor

    def contribute_to_class(self, cls, name):
        self.name = name
        models.signals.class_prepared.connect(self.finalize, sender=cls)

    def finalize(self, sender, **kwargs):
        self.ctModel = self.create_model(sender)

        # The ClosureTable object will be discarded,
        # so the signal handler can't use weak references.
        models.signals.post_save.connect(self.post_save, sender=sender, weak=False)

        descriptor = self.descriptor(self.ctModel)
        setattr(sender, self.name, descriptor)  

    def create_model(self, model):
        attrs = {'__module__': model.__module__}
        class Meta: pass
        Meta.__dict__.update(attrs)
        Meta.__dict__.update(self.get_options(model))
        attrs['Meta'] = Meta
        attrs.update(self.get_fields(model))
        name = '%s_ct_%s' % (model._meta.object_name, self.name.lower())
        return type(name, (models.Model,), attrs)

    def get_fields(self, model):
        return {
            'ancestor' : models.ForeignKey(model, related_name='+',
                                           on_delete=models.CASCADE,
                                           blank=False, null=False),
            'descendant' : models.ForeignKey(model, related_name='+',
                                             on_delete=models.CASCADE,
                                             blank=False, null=False),
            'path_length' : models.PositiveIntegerField(default=0,
                                                        blank=False, null=False),
        }

    def get_options(self, model):
        return { 'unique_together' : ('ancestor', 'descendant'), }

    def post_save(self, sender, instance, created, raw, **kwargs):
        if not raw and created:
            node = self.ctModel(ancestor=instance, descendant=instance, path_length=0)
            node.save()
