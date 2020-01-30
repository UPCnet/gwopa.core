# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from geojson import Feature
from geojson import FeatureCollection
from geojson import Point
from plone import api

from gwopa.core import _
from gwopa.core.utils import getTitleAttrLang

from five import grok
from zope.interface import Interface
from Products.CMFPlone.interfaces import IPloneSiteRoot
from datetime import datetime
import json

class debug(grok.View):
    """ Convenience view for faster debugging. Needs to be manager. """
    grok.context(Interface)
    grok.require('cmf.ManagePortal')

    def render(self):
        import ipdb; ipdb.set_trace()  # Magic! Do not delete!!! :)


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
        attr_lang = getTitleAttrLang()
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
                title=getattr(item, attr_lang),
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

    def getBudgetLimits(self):
        items = api.content.find(portal_type="Project")
        values = []
        for item in items:
            value = item.getObject().total_budget
            if value and value != 0:
                values.append(int(value / 100) * 100)
        values.sort()
        if values == []:
            values = [0, 0]
        else:
            values.append(int(values[-1:][0]) + 100)
        return {'start': values[0], 'end': values[-1:][0]}

class cron_reports(grok.View):
    """ Projects to send email report."""

    grok.context(IPloneSiteRoot)
    grok.name('cron_reports')
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        list_emails_report = []
        list_generate_report = []
        now = datetime.now()
        current_day = now.strftime("%B %d, %Y")
        #current_day = 'April 17, 2020'
        projects = api.content.find(portal_type="Project")
        for project in projects:
            try:
                for result in project.gwopa_reporting:
                    if current_day == result['date_email_report']:
                        list_emails_report.append(result)
                    if current_day == result['date_generate_report']:
                        list_generate_report.append(result)
            except:
                pass

        list_cron_reports = {'list_emails_report': list_emails_report,
                             'list_generate_report': list_generate_report}

        return json.dumps(list_cron_reports)
