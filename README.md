# All By Myself

*allbymyself* provides an abstract singleton base model along with a model admin. Singletons are classes that can only be instantiated once. 


### Quick Start

Add *allbymyself* to your `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'allbymyself',
]
```

Create a model in your `models.py` and inherit from `SingletonBaseModel`:
```python
from django.db import models
from allbymyself.models import SingletonBaseModel

class SiteSettings(SingletonBaseModel):
    site_title = models.CharField(max_length=50)
    about = models.CharField(max_length=255)
```

Register your model in the admin site, inheriting from `SingletonBaseModelAdmin`:
```python
from django.contrib import admin
from allbymyself.admin import SingletonBaseModelAdmin
from myapp.models import SiteSettings

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonBaseModelAdmin):
    fields = ('site_title', 'about')

```
