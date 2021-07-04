from django.db import models
from django.core.cache import cache
from django.urls import reverse

SINGLETON_PK = 1

class SingletonBaseModel(models.Model):
    """
    Provides an abstract model for maintaining a singleton design pattern.
    Subclass this class to create a singleton object.

    Superclass
    ----------
    models.Model

    """

    class Meta:
        abstract = True

    @classmethod
    def exists(cls):
        """
        Used to evaluate whether or not the singleton object exists in the
        database.
        
        Returns
        -------
        True : bool
            If object exists in database.

        False : bool
            If object does not exist in database.

        """

        return cls.objects.filter(pk=SINGLETON_PK).exists()

    @classmethod
    def get(cls):
        """
        Either retrieves the object from the cache (if it has been previously
        cached) or a new/existing instance. If the object is not retrieved
        from the cache, the new/existing object will be set into the cache.

        Returns
        -------
        SingletonBaseModel (subclass)
            The singleton object.

        """

        key = cls.get_cache_key()
        cached_obj = cache.get(key)
        if cached_obj is not None:
            # object found in cache, return it
            return cached_obj
        else: 
            # object not found in cache, get/create it, then set to cache
            instance, created = cls.objects.get_or_create(pk=SINGLETON_PK)
            instance._cache()
            return instance

    @classmethod
    def get_cache_key(cls):
        """
        Constructs the cache key for the object using 'cached_singleton' as the
        key's prefix and the lowercase class name of the object as the key's
        suffix.

        Example
        -------
        >>> class MyModel(SingletonBaseModel):
        >>>     pass
        
        >>> MyModel.get_cache_key()
        'cached_singleton:mymodel'
        
        Returns
        -------
        str
            The cache key.

        """

        prefix = 'cached_singleton'
        suffix = cls.__name__.lower()
        return f'{prefix}:{suffix}'

    def save(self, *args, **kwargs):
        """
        Saves the singleton object. The 'pk' field is set to 'SINGLETON_PK' to
        ensure that only one instance exists at all times. The object is also
        cached after saving is complete.
        
        """

        self.pk = SINGLETON_PK
        super().save(*args, **kwargs)
        self._cache()

    def delete(self, *args, **kwargs):
        """
        Deletes the singleton object. Before deletion, the object is removed
        from the cache.

        Returns
        -------
        django.db.models.Model.delete()

        """

        self._uncache()
        return super().delete(*args, **kwargs)

    def _cache(self):
        """
        Sets the object into the cache.

        """

        key = self.get_cache_key()
        cache.set(key, self)

    def _uncache(self):
        """
        Removes the object from the cache.

        Returns
        -------
        bool
            'True' if the deletion was successful, 'False' otherwise.

        """

        key = self.get_cache_key()
        return cache.delete(key)

    def __str__(self):
        """
        String representation of the object.

        Returns
        -------
        str
            The string representation.

        """

        return self.__class__.__name__
