from django.contrib import admin
from django.core.cache import cache
from django.test import TestCase
from allbymyself.models import SingletonBaseModel, SINGLETON_PK
from allbymyself.tests.models import SingletonTestModel

def cache_retrieve():
    cache_key = SingletonTestModel.get_cache_key()
    return cache.get(cache_key)

class SingletonTestCase(TestCase):
    def setUp(self):
        SingletonTestModel.objects.all().delete()

    def test_subclass(self):
        self.assertTrue(issubclass(SingletonTestModel, SingletonBaseModel))

    def test_abstract(self):
        with self.assertRaises(TypeError):
            abstract_instance = SingletonBaseModel()
            
    def test_pk(self):
        SingletonTestModel.objects.create(pk=SINGLETON_PK)

        instance = SingletonTestModel.objects.get(pk=SINGLETON_PK) 
        self.assertEqual(instance.pk, SINGLETON_PK)

    def test_get_does_not_exist(self):
        instance = SingletonTestModel.get()
        instance.save()
        self.assertEqual(SingletonTestModel.objects.count(), 1)
    
    def test_get_already_exists(self):
        instance = SingletonTestModel.objects.create(pk=SINGLETON_PK)
        self.assertEqual(SingletonTestModel.get(), instance)
        self.assertEqual(SingletonTestModel.objects.count(), 1)

    def test_exists(self):
        instance = SingletonTestModel.objects.create()
        self.assertTrue(SingletonTestModel.exists())

    def test_cache(self):
        instance = SingletonTestModel.objects.create(pk=SINGLETON_PK)

        instance._cache()
        cache_result = cache_retrieve()

        self.assertIsNotNone(cache_result)
        self.assertEqual(cache_result, instance)

    def test_uncache(self):
        instance = SingletonTestModel.objects.create(pk=SINGLETON_PK)
        instance._cache()

        uncached = instance._uncache()
        self.assertTrue(uncached)

        cache_result = cache_retrieve()
        self.assertIsNone(cache_result)

    def test_delete_uncache(self):
        instance = SingletonTestModel.get()
        instance.delete()

        cache_result = cache_retrieve()
        self.assertIsNone(cache_result)

    def test_delete(self):
        instance = SingletonTestModel.objects.create(pk=SINGLETON_PK)
        instance.delete()
        
        self.assertEqual(SingletonTestModel.objects.count(), 0)
