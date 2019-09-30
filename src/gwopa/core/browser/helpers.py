# -*- coding: utf-8 -*-
from five import grok
from zope.interface import Interface
from zope.interface import alsoProvides




class monitoringView(grok.View):
    """ Convenience view for monitoring software """
    grok.name('ping')
    grok.context(Interface)
    grok.require('zope2.View')

    def render(self):
        return '1'

