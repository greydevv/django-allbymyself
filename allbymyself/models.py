from django.db import models
from django.core.cache import cache
from django.urls import reverse

SINGLETON_PK = 1

class SingletonBaseModel(models.Model):
    class Meta:
        abstract = True
        # handle verbose_name_plural by default

    @classmethod
    def exists(cls):
        return cls.objects.filter(pk=SINGLETON_PK).exists()

    @classmethod
    def get(cls):
        key = cls.get_cache_key()
        cached_obj = cache.get(key)
        if cached_obj is not None:
            return cached_obj
        else: 
            instance, created = cls.objects.get_or_create(pk=SINGLETON_PK)
            if not created:
                # if object already exists, cache it
                instance._cache()
            return instance

    @classmethod
    def get_cache_key(cls):
        prefix = 'cached_singleton'
        suffix = cls.__name__.lower()
        return f'{prefix}:{suffix}'

    @classmethod
    def is_default_available(cls):
        return True

    def save(self, *args, **kwargs):
        self.pk = SINGLETON_PK
        super().save(*args, **kwargs)
        self._cache()

    def delete(self, *args, **kwargs):
        key = self.get_cache_key()
        self._uncache()
        super().delete(*args, **kwargs)

    def _uncache(self):
        key = self.get_cache_key()
        return cache.delete(key)

    def _cache(self):
        key = self.get_cache_key()
        cache.set(key, self)

    def __str__(self):
        return self.__class__.__name__
