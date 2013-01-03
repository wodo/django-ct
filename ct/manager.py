from django.db import models

__all__ = []

class Descriptor(object):

    def __init__(self, ctModel):
        self._ctModel = ctModel

    def __get__(self, instance, owner):
        if instance is None:
            return ClassManager(self._ctModel)
        return InstanceManager(self._ctModel, instance)

class ClassManager(object):

    def __init__(self, ctModel):
        self._ctModel = ctModel

class InstanceManager(object):

    def __init__(self, ctModel, instance):
        self._ctModel = ctModel
        self._instance = instance
