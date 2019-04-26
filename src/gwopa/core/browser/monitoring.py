# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
#import datetime
from gwopa.core import _


@implementer(IPublishTraverse)
class monitoringView(BrowserView):
    """ Planning View """

    index = ViewPageTemplateFile("templates/monitoring.pt")

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(monitoringView, self).__init__(context, request)
        self.year = None
        path_ordered = request.path[-1:]
        # get all param in the path -> the year /monitoring/2019
        self.year = '/'.join(path_ordered)

    def getYear(self):
        return self.year

    def getFaseStart(self):
        return self.fase_start

    def getFaseEnd(self):
        return self.fase_end

    def __call__(self):
        if not self.year or self.year == '0':
            # Empty query or 0 returns default template
            self.year = '1'
            self.fase_start = self.context.gwopa_year_phases[int(self.year) - 1]['start']
            self.fase_end = self.context.gwopa_year_phases[int(self.year) - 1]['end']
            return self.index()
        else:
            try:
                self.year = int(self.year)
            except:
                self.year = 1
            if self.year > len(self.context.gwopa_year_phases):
                self.year = 1
                self.fase_start = self.context.gwopa_year_phases[int(self.year) - 1]['start']
                self.fase_end = self.context.gwopa_year_phases[int(self.year) - 1]['end']
            else:
                self.fase_start = self.context.gwopa_year_phases[int(self.year) - 1]['start']
                self.fase_end = self.context.gwopa_year_phases[int(self.year) - 1]['end']
            return self.index()
        # TODO: if copy or delete make action!

    def getPhases(self):
        return len(self.context.gwopa_year_phases)

    def getItems(self):
        """ Returns all the project years of the monitoring """
        items = len(self.context.gwopa_year_phases)
        results = []
        total = 0

        while total != items:
            if (total == 0) and (self.request.steps[-1] == 'monitoring'):
                classe = 'disabled'
            elif self.request.steps[-1] == str(total + 1):
                classe = 'disabled'
            else:
                classe = 'visible'
            if total == 0:
                url = self.context.absolute_url_path() + '/monitoring/'
            else:
                url = self.context.absolute_url_path() + '/monitoring/' + str(total + 1)
            results.append(dict(
                title='Project Year ' + str(total + 1),
                url=url,
                alt=_(u'Show planning of year ') + str(total + 1),
                classe=classe))
            total = total + 1
        return sorted(results, key=itemgetter('title'), reverse=False)

    def getAreas(self):
        """ Returns all the Improvement Areas in a Project """
        items = api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context)
        results = []
        for project in items:
            item = project.getObject()
            results.append(dict(title=item.title,
                                url='/'.join(item.getPhysicalPath()),
                                id=item.id,
                                description=item.description,
                                portal_type=item.portal_type
                                ))
        return sorted(results, key=itemgetter('title'), reverse=False)

    def indicatorsInside(self, item):
        """ returns objects from first level (elements inside ImprovementArea) """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        data_year = self.context.gwopa_year_phases[int(self.year) - 1]
        # start = datetime.datetime.strptime(data_year['start_iso'], '%Y-%d-%m')
        # end = datetime.datetime.strptime(data_year['end_iso'], '%Y-%d-%m')
        # date_range_query = {'query': (start, end), 'range': 'min:max'},
            # start=date_range_query,
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            path={'query': folder_path,
                  'depth': 1})
        # date_range_query = {'query': (end, end), 'range': 'max'}
        #     end=date_range_query,
        outputs = portal_catalog.unrestrictedSearchResults(
            portal_type=['Output'],
            path={'query': folder_path,
                  'depth': 1})
        items = items + outputs
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in items:
            obj = item.getObject()
            annotations = IAnnotations(item.getObject())
            if KEY in annotations.keys():
                if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
                    target_value_real = ''
                    target_value_planned = _(u"Not defined")
                    unit = ''
                else:
                    target_value_real = annotations[KEY]['real']
                    target_value_planned = annotations[KEY]['planned']
                    unit = obj.measuring_unit
            else:
                target_value_real = ''
                target_value_planned = _(u"Not defined")
                unit = ''
            if not item.start:
                item.start = '-----'
            if not item.end:
                item.end = '-----'
            results.append(dict(
                title=item.Title,
                portal_type=item.portal_type,
                start=item.start,
                end=item.end,
                unit=unit,
                target_value_real=target_value_real,
                target_value_planned=target_value_planned,
                year='-----',
                next_update=data_year['end_iso'],
                url='/'.join(obj.getPhysicalPath())))
        return results

    def listOutcomesKPI(self):
        items = api.content.find(
            portal_type=['OutcomeKPI', 'OutcomeZONE'],
            context=self.context)
        results = []
        for item in items:
            members = []
            obj = item.getObject()
            if obj.members:
                users = obj.members
                for member in users:
                    members.append(api.user.get(username=member).getProperty('fullname'))
            results.append(dict(
                title=item.Title,
                description=item.Description,
                base_date=obj.baseline_date,
                base_value='baseline_value',
                target_value='target_value',
                measuring_unit=obj.measuring_unit,
                measuring_frequency=obj.measuring_frequency,
                portal_type=item.portal_type,
                responsible=members,
                url='/'.join(obj.getPhysicalPath())))
        return results

    def listOutcomesCC(self):
        items = api.content.find(
            portal_type=['OutcomeCC', 'OutcomeCCS'],
            context=self.context)
        results = []
        for item in items:
            obj = item.getObject()
            if obj.aq_parent.portal_type == 'ImprovementArea':
                area = obj.aq_parent.title
            else:
                area = obj.aq_parent.aq_parent.title
            results.append(dict(
                area=area,
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url='/'.join(obj.getPhysicalPath())))
        return results
