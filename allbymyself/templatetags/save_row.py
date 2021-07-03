from django import template
from django.template.context import Context
from django.contrib.admin.templatetags.base import InclusionAdminNode

register = template.Library()

def save_row(context):
    add = context['add']
    change = context['change']
    is_popup = context['is_popup']
    show_save = context.get('show_save', True)
    show_save_and_continue = context.get('show_save_and_continue', True)
    has_add_permission = context['has_add_permission']
    has_change_permission = context['has_change_permission']
    has_view_permission = context['has_view_permission']
    has_editable_inline_admin_formsets = context['has_editable_inline_admin_formsets']
    can_save = (has_change_permission and change) or (has_add_permission and add) or has_editable_inline_admin_formsets
    can_save_and_continue = not is_popup and can_save and has_view_permission and show_save_and_continue
    can_change = has_change_permission or has_editable_inline_admin_formsets
    ctx = Context(context)
    ctx.update({
        'can_change': can_change,
        'show_delete_link': (
            not is_popup and context['has_delete_permission'] and
            change and context.get('show_delete', True)
        ),
        'show_save_and_continue': can_save_and_continue,
        'show_save': show_save and can_save,
        'show_close': not(show_save and can_save)
    })
    return ctx

@register.tag(name='save_row')
def save_row_tag(parser, token):
    return InclusionAdminNode(parser, token, func=save_row, template_name='save_row.html')
