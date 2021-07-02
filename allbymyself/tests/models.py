from apps.allbymyself.models import SingletonBaseModel

class SingletonTestModel(SingletonBaseModel):
    pass

class SingletonTestModelAvailable(SingletonBaseModel):
    @classmethod
    def is_default_available(cls):
        return True
