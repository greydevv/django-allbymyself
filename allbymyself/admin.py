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
    """
    Admin model for subclasses of SingletonBaseModel. Subclass this model
    to provide custom functionality to control how subclasses of
    SingletonBaseModel are operated upon via the admin interface.

    Superclass
    ----------
    admin.ModelAdmin

    """

    change_form_template = 'admin/singleton_change_form.html'
    object_history_template = 'admin/singleton_object_history.html'

    def has_add_permission(self, *args, **kwargs):
        """
        Specifies whether or not the registered model is able to be added or
        not.

        Returns
        -------
        bool
            'True' if the model exists, 'False' otherwise.
            
        """

        return not self.model.exists()
    
    def has_delete_permission(self, *args, **kwargs):
        """
        Specifies whether or not the registered model is able to be deleted or
        not.

        Returns
        -------
        bool
            'True' if the model is able to be deleted, 'False' otherwise. By
            default, 'False' is returned as singleton objects should not, in
            most cases, be deleted.

        """

        return False

    def is_default_available(self):
        """
        Specifies whether or not an instance of the registered model is created
        by default in the admin interface.

        Returns
        -------
        bool
            'True' if an instance and created by default, 'False' otherwise. By
            default, 'False' is returned.

        """

        return False
    
    def get_urls(self):
        """
        Administration URLs for the registered model. Here, the change view is
        mapped to '', which effectively skips the change list page. The
        history view is mapped to 'history/'. Both of these URL mappings
        eliminate the object's id from the URL as a singleton is only
        ever going to have one instane in existence. 

        Returns
        -------
        list of django.urls.resolver.URLPattern
            Custom change view and history view mappings prepended to the
            default URLs coming from 'admin.ModelAdmin'.

        """

        def wrap(view):
            def wrapper(*args, **kwargs):
                # send arguments to wrapped view
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)
        
        if self.is_default_available() and not self.model.exists():
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
        """
        Called after the administrator changes the registered model. If the
        model does not exist, 'SingletonBaseModelAdmin.add_view' is called from
        ths method instead.

        Parameters
        ----------
        request : django.core.handlers.wsgi.WSGIRequest
            The incoming change request.
        obj : SingletonBaseModel (subclass)
            The obejct that the view is being rendered for.

        Returns
        -------
        SingletonBaseModelAdmin.add_view()
            If the model does not exist.
        django.contrib.admin.options.ModelAdmin.change_view()
            If the model exists.

        """

        if not self.model.exists():
            return self.add_view(request, form_url, extra_context)
        else:
            return super().change_view(request, object_id, form_url, extra_context)

    def response_change(self, request, obj):
        """
        Called after the administrator changes the registered model.

        Parameters
        ----------
        request : django.core.handlers.wsgi.WSGIRequest
            The incoming change request.
        obj : SingletonBaseModel (subclass)
            The object being changed.

        Returns
        -------
        SingletonBaseModelAdmin._save_response()
            If the save type is '_save'.

        django.contrib.admin.options.ModelAdmin.response_add()
            If the save type is anything but '_save'.

        """

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
        """
        Determines the response type of the add view stage.

        Parameters
        ----------
        request : django.core.handlers.wsgi.WSGIRequest
            Incoming add request.
        obj : SingletonBaseModel (subclass)
            Object being added.
        post_url_continue : django.urls.resolvers.URLResolver
            URL to redirect to.

        Returns
        -------
        SingletonBaseModelAdmin._save_response()
            If the save type is '_save'.
            
        django.contrib.admin.options.ModelAdmin.response_add()
            If the save type is anything but '_save'.

        """

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
        """
        Responsible for displaying a success message to the user and redirecting
        them to the admin index page after adding or changing the registered
        model.

        Returns
        -------
        django.http.HttpRespone
            The admin index page, returned via 'django.shortcuts.redirect'

        """

        self.message_user(request, msg, messages.SUCCESS)
        redirect_url = reverse('admin:index')
        return redirect(redirect_url)
