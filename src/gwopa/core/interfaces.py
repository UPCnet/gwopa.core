# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface

class IGwopaCoreLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IGwopaUtils(Interface):
    """ Marker describing the functionality of the convenience methods
        placeholder ulearn.utils view.
    """