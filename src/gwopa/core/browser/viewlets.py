# -*- coding: utf-8 -*-
from five import grok
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalHeader
from zope.interface import Interface

from gwopa.core.interfaces import IGwopaCoreLayer


grok.context(Interface)


class viewletBase(grok.Viewlet):
    grok.baseclass()


class viewletHeader(viewletBase):
    grok.name('gwopa.header')
    grok.template('header')
    grok.viewletmanager(IPortalHeader)
    grok.layer(IGwopaCoreLayer)

    def isRootFolder(self):
        if (self.context.portal_type != 'Plone Site'):
            return True
        else:
            return False


class viewletFooter(viewletBase):
    grok.name('gwopa.footer')
    grok.template('footer')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IGwopaCoreLayer)
