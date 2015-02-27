"""artlassya templatetags"""

from django.utils.encoding import force_bytes, force_str
from django import template

import binascii


register = template.Library()


@register.filter
def hexencode(unencoded_string):
    return "".join(["%" + force_str(binascii.hexlify(force_bytes(char))) 
                    for char in unencoded_string])
# /hexencode


#EOF - artlassya templatetags