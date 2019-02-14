# -*- coding: utf-8 -*-
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from gwopa.core.content.project import IProject
from plone.app.layout.navigation.root import getNavigationRootObject
from Acquisition import aq_inner


class ISideNavPortlet(IPortletDataProvider):
    """ GWOPA SIDE NAVIGATION """


@implementer(ISideNavPortlet)
class Assignment(base.Assignment):

    title = _(u'gwopa_menu', default=u'GWOPA Menu')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('sidenav.pt')

    def isRootFolder(self):
        if (self.context.portal_type != 'Plone Site'):
            return True
        else:
            return False

    def projectPath(self):
        if IProject.providedBy(self.context):
            return self.context.absolute_url()
        else:
            try:
                portal_state = self.context.restrictedTraverse('@@plone_portal_state')
                root = getNavigationRootObject(self.context, portal_state.portal())
                physical_path = aq_inner(self.context).getPhysicalPath()

                relative = physical_path[len(root.getPhysicalPath()):]

                for i in range(len(relative)):
                    now = relative[:i + 1]
                    obj = aq_inner(root.restrictedTraverse(now))
                    if IProject.providedBy(obj):
                        return obj.absolute_url()
            except:
                return None

        return None


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
