# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot

from five import grok
from plone import api

from gwopa.core.interfaces import IGwopaCoreLayer
from gwopa.core.utils import getTitleAttrLang

import requests

requests.packages.urllib3.disable_warnings()

grok.templatedir("templates")


class managePortal(grok.View):
    grok.name('managePortal')
    grok.template('manage_portal')
    grok.context(IPloneSiteRoot)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.AddPortalMember')

    def getProjects(self):
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            project = item.getObject()
            results.append(dict(
                title=item.Title,
                start=project.startactual.strftime('%Y-%m-%d'),
                end=project.completionactual.strftime('%Y-%m-%d'),
                manager=project.project_manager_admin,
                country=project.country,
                url='/'.join(project.getPhysicalPath())))
        return results

    def getAreas(self):
        attr_lang = getTitleAttrLang()
        items = api.content.find(portal_type=['ImprovementArea'])
        results = []
        for item in items:
            obj = item.getObject()
            results.append(dict(
                title=getattr(item, attr_lang),
                parent=obj.aq_parent.title,
                url='/'.join(obj.getPhysicalPath())))
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
            if obj.region and len(obj.region) > 1:
                region = ', '.join(map(str, obj.region))
            elif obj.region:
                region = str(obj.region[0])
            else:
                region = ''
            results.append(dict(
                title=item.Title,
                url='/'.join(obj.getPhysicalPath()),
                country=', '.join(map(str, obj.country)),
                region=region)
            )
        return results

    def getPrograms(self):
        items = api.content.find(portal_type=['Program'])
        results = []
        for item in items:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                url='/'.join(obj.getPhysicalPath()),
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
                url='/'.join(obj.getPhysicalPath()),
                country=', '.join(map(str, obj.country)),
                contact=obj.contact)
            )
        return results

    def getDonors(self):
        items = api.content.find(portal_type=['Donor'])
        results = []
        for item in items:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                url='/'.join(obj.getPhysicalPath()),
                country=', '.join(map(str, obj.country)),
                contact=obj.contact)
            )
        return results
