# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api
from geojson import Feature, Point, FeatureCollection
from gwopa.core import _
import transaction
from Products.statusmessages.interfaces import IStatusMessage


class listFiles(BrowserView):
    """ View all the files associated to the project.
        Separated by area.
        If this is a root call, shows all site files
    """
    __call__ = ViewPageTemplateFile('templates/files.pt')

    def isRootFolder(self):
        if (self.context.portal_type != 'Plone Site'):
            return _(u'Here are the files of the Project.')
        else:
            return _(u'Here are all files of the Platform.')

    def all_files(self):
        if self.context.portal_type == 'Project':
            items = api.content.find(
                portal_type=['File'],
                path='/'.join(self.context.getPhysicalPath()))
        else:
            items = api.content.find(portal_type=['File'])
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
            if obj.geolocation:
                if obj.geolocation.longitude and obj.geolocation.latitude:
                    poi = Feature(geometry=Point((obj.geolocation.longitude, obj.geolocation.latitude)), properties={'popup': obj.title})
                    results.append(poi)
        return FeatureCollection(results)


class Delete(BrowserView):
    """ Delete elements from year XXX """
    def __call__(self):
        messages = IStatusMessage(self.request)
        year = int(self.request.form['id'])
        items = api.content.find(
            portal_type=['Activity', 'Output'],
            context=self.context,
            gwopa_year=year)
        for item in items:
            elem = item.getObject()
            api.content.delete(obj=elem)
            transaction.commit()
        message = _(u"Workplan deleted from year: ") + str(year)
        messages.addStatusMessage(message, type="info")
        self.request.response.redirect('/'.join(self.context.getPhysicalPath()) + '/planning')


class Copy(BrowserView):
    """ Copy  elements from year XXX """
    def __call__(self):
        messages = IStatusMessage(self.request)
        year = int(self.request.form['id'])
        items = api.content.find(
            portal_type=['Activity', 'Output'],
            context=self.context,
            gwopa_year=year)
        for item in items:
            elem = item.getObject()
            obj = api.content.copy(source=elem, target=elem.aq_parent, safe_id=True)
            obj.gwopa_year = int(year) + 1
            transaction.commit()
        message = _(u"Workplan duplicated.")
        messages.addStatusMessage(message, type="info")
        self.request.response.redirect('/'.join(self.context.getPhysicalPath()) + '/planning')
