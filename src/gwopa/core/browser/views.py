# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api
import json
from geojson import Feature, Point, FeatureCollection


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
                url='/'.join(item.getPhysicalPath())))
        return results


class listAreas(BrowserView):
    """ View all the Areas associated to the project.
        Separated by area.
    """
    __call__ = ViewPageTemplateFile('templates/areas.pt')

    def getTitle(self):
        return self.context.Title()

    def allfiles(self):
        items = api.content.find(portal_type=['ImprovementArea'])
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url='/'.join(item.getPhysicalPath())))
        return results


class listTeam(BrowserView):
    """ View all the People associated to the project.
        Separated by area.
    """
    __call__ = ViewPageTemplateFile('templates/teams.pt')

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
                url='/'.join(item.getPhysicalPath())))
        return results


class select2(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type=['Project', 'ImprovementArea'])
        results = []
        for item in items:
            results.append(dict(
                id=item.id,
                text=item.Title))
        return json.dumps(
            {
                'placeholder': "Select a Category",
                'results': results,
            }
        )


class mapView(BrowserView):
    """ Generate valid json to show POI in map """
    __call__ = ViewPageTemplateFile('templates/global_map.pt')

    def getPoints(self):
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            obj = item.getObject()
            if obj.geolocation:
                if obj.geolocation.longitude and obj.geolocation.latitude:
                    poi = Feature(geometry=Point((obj.geolocation.longitude, obj.geolocation.latitude)), properties={'popup': obj.title})
                    results.append(poi)
        return FeatureCollection(results)
