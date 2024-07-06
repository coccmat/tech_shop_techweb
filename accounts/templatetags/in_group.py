from django import template

register = template.Library() 

@register.filter(name='in_group') 
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists() 