# -*- coding: utf-8 -*-
from five import grok
from plone import api
from Products.CMFPlone.interfaces import IPloneSiteRoot
from gwopa.core.interfaces import IGwopaCoreLayer
import requests
requests.packages.urllib3.disable_warnings()

grok.templatedir("templates")


class managePortal(grok.View):
    grok.name('managePortal')
    grok.template('manage_portal')
    grok.context(IPloneSiteRoot)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.ManagePortal')

    def getProjects(self):
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            project = item.getObject()
            results.append(dict(
                title=item.Title,
                start=item.start,
                end=item.end,
                manager=project.project_manager_admin,
                country=project.country,
                url=item.getPath()))
        return results

    def getAreas(self):
        items = api.content.find(portal_type=['ImprovementArea'])
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                parent=item.getObject().aq_parent.title,
                url=item.getPath()))
        return results

    def getUsers(self):
        members = api.user.get_users()
        results = []

        for item in members:
            results += [{'id': item.id,
                         }]
        return results

    def getPlatforms(self):
        items = api.content.find(portal_type=['Platform'])
        results = []
        for item in items:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                url=item.getPath(),
                country=', '.join(map(str, obj.country)))
            )
        return results

    def getPrograms(self):
        items = api.content.find(portal_type=['Program'])
        results = []
        for item in items:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                url=item.getPath(),
                email=obj.contact,
                country=', '.join(map(str, obj.country)))
            )
        return results

    def getPartners(self):
        items = api.content.find(portal_type=['Partner'])
        results = []
        for item in items:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                url=item.getPath(),
                country=', '.join(map(str, obj.country)))
            )
        return results
