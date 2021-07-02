from functools import update_wrapper
from urllib.parse import quote as urlquote
from django.utils.translation import gettext as _
from django.utils.html import format_html
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from allbymyself.models import SINGLETON_PK
from allbymyself.path_utils import get_path_name

class SingletonBaseModelAdmin(admin.ModelAdmin):
    change_form_template = 'admin/singleton_change_form.html'
    object_history_template = 'admin/singleton_object_history.html'

    def has_add_permission(self, *args, **kwargs):
        return not self.model.exists()
    
    def has_delete_permission(self, *args, **kwargs):
        return False
    
    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                # send arguments to wrapped view
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)
        
        if self.model.is_default_available() and not self.model.exists():
            # get or create singleton if it should be available by default
            self.model.get()

        singleton_urls = [
            path(
                # skips object list view and directs change view
                # http://127.0.0.1:8000/appname/model
                route = '',
                view = wrap(self.change_view),
                kwargs = {'object_id': str(SINGLETON_PK)},
                name = get_path_name(self.model, 'change'),
            ),
            path(
                # history url - no need for object id in url
                # http://127.0.0.1:8000/appname/model/history
                route = 'history/',
                view = wrap(self.history_view),
                kwargs = {'object_id': str(SINGLETON_PK)},
                name = get_path_name(self.model, 'history'),
            ),
        ]

        urls = super().get_urls()
        return singleton_urls + urls

    def change_view(self, request, object_id, form_url='', extra_context=None):
        if not self.model.exists():
            return self.add_view(request, form_url, extra_context)
        else:
            return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        if '_save' in request.POST:
            opts = self.model._meta
            # result of obj.__str__ will be placed into message
            msg_dict = {
                'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), str(obj))
            }
            msg = format_html(
                _('{obj} was changed successfully.'),
                **msg_dict
            )
            return self._save_response(request, obj, msg)
        else:
            return super().response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if '_save' in request.POST:
            opts = self.model._meta
            # obj.__str__() will be placed into message
            msg_dict = {
                'obj': format_html('<a href="{}">{}</a>', urlquote(request.path), obj)
            }
            msg = format_html(
                _('{obj} was added successfully.'),
                **msg_dict
            )
            return self._save_response(request, obj, msg)
        else:
            return super().response_add(request, obj, post_url_continue)

    def _save_response(self, request, obj, msg):
        self.message_user(request, msg, messages.SUCCESS)
        redirect_url = reverse('admin:index')
        return redirect(redirect_url)
