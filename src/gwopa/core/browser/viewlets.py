# -*- coding: utf-8 -*-
from five import grok
from plone.app.layout.viewlets.interfaces import IPortalFooter
from zope.interface import Interface
from gwopa.core.interfaces import IGwopaCoreLayer

grok.context(Interface)


class viewletBase(grok.Viewlet):
    grok.baseclass()


class viewletFooter(viewletBase):
    grok.name('gwopa.footer')
    grok.template('footer')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IGwopaCoreLayer)
