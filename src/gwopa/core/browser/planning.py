# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
import datetime


@implementer(IPublishTraverse)
class planningView(BrowserView):
    """ Planning View """

    index = ViewPageTemplateFile("templates/planning.pt")

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(planningView, self).__init__(context, request)
        self.year = None
        path_ordered = request.path[-1:]
        # get all param in the path -> the year /planning/2019
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
            self.fase_start = self.context.gwopa_fases[int(self.year) - 1]['start']
            self.fase_end = self.context.gwopa_fases[int(self.year) - 1]['end']
            return self.index()
        else:
            try:
                self.year = int(self.year)
            except:
                self.year = 1
            if self.year > len(self.context.gwopa_fases):
                self.year = 1
                self.fase_start = self.context.gwopa_fases[int(self.year) - 1]['start']
                self.fase_end = self.context.gwopa_fases[int(self.year) - 1]['end']
            else:
                self.fase_start = self.context.gwopa_fases[int(self.year) - 1]['start']
                self.fase_end = self.context.gwopa_fases[int(self.year) - 1]['end']
            return self.index()
        # TODO: if copy or delete make action!

    def getItems(self):
        """ Returns all the project years of the planning """
        items = len(self.context.gwopa_fases)
        results = []
        total = 0

        while total != items:
            if (total == 0) and (self.request.steps[-1] == 'planning'):
                classe = 'disabled'
            elif self.request.steps[-1] == str(total + 1):
                classe = 'disabled'
            else:
                classe = 'visible'
            if total == 0:
                url = self.context.absolute_url_path() + '/planning/'
            else:
                url = self.context.absolute_url_path() + '/planning/' + str(total + 1)
            results.append(dict(
                title='Project Year ' + str(total + 1),
                url=url,
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
                                description=item.description,
                                portal_type=item.portal_type
                                ))
        return results

    def indicatorsInside(self, item):
        """ returns objects from first level (elements inside ImprovementArea) """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        data_year = self.context.gwopa_fases[int(self.year) - 1]
        start = datetime.datetime.strptime(data_year['start_iso'], '%Y-%d-%m')
        end = datetime.datetime.strptime(data_year['end_iso'], '%Y-%d-%m')
        date_range_query = {'query': (start, end), 'range': 'min:max'}
        #     start=date_range_query,
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            path={'query': folder_path,
                  'depth': 1})
        # date_range_query = {'query': (end, end), 'range': 'max'}
            # end=date_range_query,
        outputs = portal_catalog.unrestrictedSearchResults(
            portal_type=['Output'],
            path={'query': folder_path,
                  'depth': 1})
        items = items + outputs
        results = []
        for item in items:
            if not item.start:
                item.start = '---'
            if not item.end:
                item.end = '---'
            if not item.getObject().members:
                members = 'None'
            else:
                members = item.getObject().members

            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                start=item.start,
                end=item.end,
                responsible=members,
                url='/'.join(item.getObject().getPhysicalPath())))
        return results

    def listOutcomesKPI(self):
        items = api.content.find(
            portal_type=['OutcomeKPI', 'OutcomeZONE'],
            context=self.context)
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url='/'.join(item.getObject().getPhysicalPath())))
        return results

    def listOutcomesCC(self):
        items = api.content.find(
            portal_type=['OutcomeCC', 'OutcomeCCS'],
            context=self.context)
        results = []
        for item in items:
            if item.getObject().aq_parent.portal_type == 'ImprovementArea':
                area = item.getObject().aq_parent.title
            else:
                area = item.getObject().aq_parent.aq_parent.title
            results.append(dict(
                area=area,
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url='/'.join(item.getObject().getPhysicalPath())))
        return results
