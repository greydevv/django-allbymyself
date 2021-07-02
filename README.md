# All By Myself

*`allbymyself`* provides an abstract singleton base model, `SingletonBaseModel`, along with a model admin, `SingletonBaseModelAdmin`. Singletons are classes that can only be instantiated once.


### Quick Start

Create a model in your `models.py` and subclass `SingletonBaseModel`:
```python
from django.db import models
from allbymyself.models import SingletonBaseModel

class SiteSettings(SingletonBaseModel):
    site_title = models.CharField(max_length=50)
    about = models.CharField(max_length=255)
```

Register the model in your `admin.py`, subclassing `SingletonBaseModelAdmin`:
```python
from django.contrib import admin
from allbymyself.admin import SingletonBaseModelAdmin
from your_app.models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonBaseModelAdmin):
    fields = ('site_title', 'about')
```

### Features

* Skips change list page and instead goes straight to the change form or add form.
* `SingletonBaseModel` handles caching and uncaching. 
* Admin URLs for change form and history form will not include object id.
* After saving changes or adding a new instance, the admin user is redirected to the admin index.
* Override `is_default_available` and return `True` to create an instance on admin page startup:
```python
class SiteSettings(SingletonBaseModel):
    site_title = models.CharField(max_length=50)
    about = models.CharField(max_length=255)

    @classmethod
    def is_default_available(cls):
        return True
```

### Context Processor

Add your instance as a context processor to make it available in all templates. First, create `context_processors.py` in your app, and add the context processor:
```python
from django.urls import reverse
from your_app.models import SiteSettings

def site_settings(request):
    if request.path.startswith(reverse('admin:index')):
        return {}
    else:
        return {'site_settings': SiteSettings.get()}
```
The above `if` statement prevents creation of an instance on admin page startup. This is only necessary if `is_default_available` returns `False`. Then, in your project's `settings.py`:
```python
TEMPLATES = [
    {
        ...
        'OPTIONS': {
            'context_processors': [
                ...
                'your_app.context_processors.site_settings',
            ],
        },
    },
]
```
