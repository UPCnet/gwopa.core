# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api
from Products.CMFCore.utils import getToolByName
import json


class listIndicators(BrowserView):
    """ View all the indicators associated to the project
    """
    __call__ = ViewPageTemplateFile('templates/indicators.pt')

    def getTitle(self):
        return self.context.Title()

    def listActivities(self):
        items = api.content.find(portal_type='Activity')
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                url=item.getPath()))
        return results

    def goalsList(self):
        items = api.content.find(portal_type='Goal')
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url=item.getPath()))
        return results

    def indicatorsInside(self, item):
        """ returns objects from first level
        """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Indicator', 'Outcome', 'Output'],
            path={'query': folder_path,
                  'depth': 1})

        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url=item.getPath()))
        return results

    def indicatorsInsideInside(self, item):
        """ Returns objects from second level, except indicators.
            Because an indicator inside an indicator is not accepted.
        """
        if item['portal_type'] != 'Indicator':
            portal_catalog = getToolByName(self, 'portal_catalog')
            folder_path = item['url']
            items = portal_catalog.unrestrictedSearchResults(
                portal_type=['Indicator'],
                path={'query': folder_path,
                      'depth': 1})
            results = []
            for item in items:
                results.append(dict(
                    title=item.Title,
                    description=item.Description,
                    portal_type=item.portal_type,
                    url=item.getPath()))
            return results


class listFiles(BrowserView):
    """ View all the files associated to the project.
        Separated by area.
        If this is a root call, shows all site files
    """
    __call__ = ViewPageTemplateFile('templates/files.pt')

    def getTitle(self):
        return self.context.Title()

    def allfiles(self):
        items = api.content.find(portal_type=['Page', 'Document'])
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url=item.getPath()))
        return results


class select2(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            results.append(dict(
                id=item.id,
                text=item.Title))
        return json.dumps({'results': results})
