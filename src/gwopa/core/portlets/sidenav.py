# -*- coding: utf-8 -*-
from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import implementer
from gwopa.core.content.project import IProject
from plone.app.layout.navigation.root import getNavigationRootObject
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner
from plone import api
#from plone.folder.interfaces import IFolder


class ISideNavPortlet(IPortletDataProvider):
    """ GWOPA SIDE NAVIGATION """


@implementer(ISideNavPortlet)
class Assignment(base.Assignment):

    title = _(u'gwopa_menu', default=u'GWOPA Menu')


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('sidenav.pt')

    def isRootFolder(self):
        if self.context.portal_type == 'Plone Site' or self.request.getURL().split('/')[-1] == '++add++Project':
            return True
        else:
            return False

    def isManager(self):
        # Can create projects
        currentuser = api.user.get_current().id
        roles = ['Manager', 'Site Administrator']
        for role in roles:
            if role in api.user.get_roles(username=currentuser):
                return True
        return False

    def projectPath(self):
        if IProject.providedBy(self.context):
            return self.context.absolute_url()
        else:
            try:
                portal_state = self.context.restrictedTraverse('@@plone_portal_state')
                root = getNavigationRootObject(self.context, portal_state.portal())
                project_path = root.absolute_url()
                physical_path = aq_inner(self.context).getPhysicalPath()
                relative = physical_path[len(root.getPhysicalPath()):]
                now = ""
                for i in range(len(relative)):
                    now += relative[i] + "/"
                    obj = aq_inner(root.restrictedTraverse(now))
                    if IProject.providedBy(obj):
                        project_path = obj.absolute_url()
                return project_path
            except:
                return None
        return None

    def selected_portal_tab(self):
        request = self.request
        return request['URL']

    def current_path(self):
        plone_url = getToolByName(self.context, 'portal_url')()
        plone_url_len = len(plone_url)
        request = self.request
        url = request['URL']
        path = url[plone_url_len:]
        return url.startswith(plone_url + path)

 
class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
