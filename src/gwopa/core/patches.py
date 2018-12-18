# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IJsonCompatible
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
import six

from plone.restapi.serializer.converters import default_converter


@adapter(Interface)
@implementer(IJsonCompatible)
def default_converter_modified(value):
    if value is None:
        return value

    if type(value) in (six.text_type, bool, int, float, int):
        return value
    # Monkeypatched to check geolocation values and return in JSON format
    if type(value).__name__ == 'Geolocation':
        return 'Latitude: ' + str(value.latitude) + ' / ' + 'Longitude: ' + str(value.longitude)

    raise TypeError(
        'No converter for making'
        ' {0!r} ({1}) JSON compatible.'.format(value, type(value)))


default_converter.func_code = default_converter_modified.func_code
