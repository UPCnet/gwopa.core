# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api
from geojson import Feature, Point, FeatureCollection
from gwopa.core import _
import transaction
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName
import json

# class listFiles(BrowserView):
#     """ View all the files associated to the project.
#         Separated by area.
#         If this is a root call, shows all site files
#     """
#     __call__ = ViewPageTemplateFile('templates/files.pt')

#     def isRootFolder(self):
#         if (self.context.portal_type != 'Plone Site'):
#             return _(u'Here are the files of the Project.')
#         else:
#             return _(u'Here are all files of the Platform.')

#     def all_files(self):
#         if self.context.portal_type == 'Project':
#             items = api.content.find(
#                 portal_type=['File'],
#                 path='/'.join(self.context.getPhysicalPath()))
#         else:
#             items = api.content.find(portal_type=['File'])
#         results = []
#         for item in items:
#             results.append(dict(
#                 title=item.Title,
#                 description=item.Description,
#                 portal_type=item.portal_type,
#                 url='/'.join(item.getPhysicalPath())))
#         return results


class listAreas(BrowserView):
    """ View all the Areas associated to the project.
        Separated by area.
    """
    __call__ = ViewPageTemplateFile('templates/areas.pt')

    def isRootFolder(self):
        if (self.context.portal_type != 'Plone Site'):
            return _(u'Here are the Improvement Areas of the Project.')
        else:
            return _(u'Here are all the Improvement Areas of the Platform.')

    def all_areas(self):
        if self.context.portal_type == 'Project':
            items = api.content.find(
                portal_type=['ImprovementArea'],
                path='/'.join(self.context.getPhysicalPath()))
        else:
            items = api.content.find(portal_type=['ImprovementArea'])
        results = []
        for item in items:
            obj = item.getObject()
            if obj.image is None:
                image = obj.absolute_url_path() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
            else:
                image = obj.absolute_url_path() + '/@@images/image/thumb'
            results.append(dict(
                title=item.Title,
                image=image,
                project=obj.aq_parent.Title(),
                url='/'.join(obj.getPhysicalPath()),
                description=item.description))
        return results


class listTeams(BrowserView):
    """ View all the People associated to the project.
        Separated by area.
    """
    __call__ = ViewPageTemplateFile('templates/teams.pt')

    def all_users(self):
        members = api.user.get_users()
        results = []

        for item in members:
            results += [{'id': item.id,
                         'project': item.getProperty('wop_programs')
                         }]
        return results

    def isProject(self):
        if (self.context.portal_type == 'Plone Site'):
            return False
        else:
            return True


class mapView(BrowserView):
    """ Generate valid json to show POI in map """
    __call__ = ViewPageTemplateFile('templates/global_map.pt')

    def getPoints(self):
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            obj = item.getObject()
            if obj.longitude and obj.latitude:
                poi = Feature(geometry=Point((float(obj.longitude), float(obj.latitude))), properties={'popup': '<a href="' + obj.absolute_url() + '">' + obj.title + '</a><br/>Status:'})
                results.append(poi)
        if results:
            return FeatureCollection(results)
        else:
            return None


class API(BrowserView):
    """ Return needed values in json format """

    def __call__(self):
        project = self.context
        results = []

        results = [{'id': project.id,
                    'title': project.title,
                    'description': project.description,
                    'status': project.status,
                    'country': project.country,
                    'category': project.category,
                    'areas': project.areas,
                    'assumptions': 'project.assumptions.output()',
                    'contribution': 'project.contribution.output()',
                    'creation_date': 'project.creation_date.strfmt()',
                    'creatorts': project.creators,
                    'currency': project.currency,
                    'phases': len(project.gwopa_fases),
                    'gwopa_fases': project.gwopa_fases,
                    'modification_date': 'project.modification_date.strfmt()',
                    'objectives': 'project.objectives.output()',
                    }]
        return json.dumps(results)
