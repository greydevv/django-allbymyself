# All By Myself - Django Singletons

Singletons are objects that can only be instantiated once and serve a specific purpose. A classic example of where a singleton is necessary in web development is site configuration.
This package provides an abstract singleton base model, `SingletonBaseModel`, along with a model admin, `SingletonBaseModelAdmin`, both of which are utilized to create and manage singleton objects in Django. 

### Installation

```bash
$ pip install django-allbymyself
```

### Quick Start

Add to `INSTALLED_APPS` in your project's `settings.py` to load custom admin templates:
```python
INSTALLED_APPS = [
    ...
    'allbymyself',
]
```

Create a model in `your_app/models.py` and subclass `SingletonBaseModel`:
```python
from django.db import models
from allbymyself.models import SingletonBaseModel

class SiteSettings(SingletonBaseModel):
    site_title = models.CharField(max_length=50)
    about = models.CharField(max_length=255)
```

Register the model in `your_app/admin.py`, subclassing `SingletonBaseModelAdmin`:
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
    site_title = models.CharField(max_length=50, blank=True)
    about = models.CharField(max_length=255, blank=True)

    @classmethod
    def is_default_available(cls):
        # if True, make sure to handle field defaults in your model
        # appropriately!
        return True
```

### Context Processor

You may also add your object as a context processor to make it available in all templates, site-wide. First create `your_app/context_processors.py` and add the following:
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

You can then access your object in your templates like any other piece of context:
```html
<h1>{{ site_settings.site_title }}</h1>
<p>{{ site_settings.about }}</p>
```

### Testing

Simply run tests like so:
```bash
$ python manage.py test allbymyself
```
