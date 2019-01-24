# -*- coding: utf-8 -*-
from five import grok
from plone.app.layout.viewlets.interfaces import IPortalFooter
from plone.app.layout.viewlets.interfaces import IPortalHeader
from zope.interface import Interface
from Products.CMFCore.utils import getToolByName

from gwopa.core.interfaces import IGwopaCoreLayer
from gwopa.core.content.project import IProject
from plone.app.layout.navigation.root import getNavigationRootObject
from Acquisition import aq_inner

grok.context(Interface)


class viewletBase(grok.Viewlet):
    grok.baseclass()


class viewletHeader(viewletBase):
    grok.name('gwopa.header')
    grok.template('header')
    grok.viewletmanager(IPortalHeader)
    grok.layer(IGwopaCoreLayer)

    def selected_portal_tab(self):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        plone_url = getNavigationRootObject(
            self.context, portal).absolute_url()
        plone_url_len = len(plone_url)
        request = self.request

        url = request['URL']
        path = url[plone_url_len:]
        path_list = path.split('/')
        return None

    def isRootFolder(self):
        if (self.context.portal_type != 'Plone Site'):
            return True
        else:
            return False

    def projectPath(self):
        if IProject.providedBy(self.context):
            return self.context.absolute_url()
        else:
            portal_state = self.context.unrestrictedTraverse('@@plone_portal_state')
            root = getNavigationRootObject(self.context, portal_state.portal())
            physical_path = aq_inner(self.context).getPhysicalPath()

            relative = physical_path[len(root.getPhysicalPath()):]

            for i in range(len(relative)):
                now = relative[:i + 1]
                obj = aq_inner(root.restrictedTraverse(now))
                if IProject.providedBy(obj):
                    return obj.absolute_url()

        return None


class viewletFooter(viewletBase):
    grok.name('gwopa.footer')
    grok.template('footer')
    grok.viewletmanager(IPortalFooter)
    grok.layer(IGwopaCoreLayer)
