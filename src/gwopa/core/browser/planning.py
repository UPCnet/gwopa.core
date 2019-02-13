# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
import datetime
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from Products.CMFCore.utils import getToolByName


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
        if len(request.path) == 2:
            if request.path[-2::-1][0] == 'delete':
                print "# Deleting year -> " + str(request.path[-1])
                self.action = 'delete'
                #deleteyear = request.path[-1]
                # portal_catalog = getToolByName(self, 'portal_catalog')
                # items = portal_catalog.unrestrictedSearchResults(
                #     portal_type=['Activity', 'Output'],
                #     gwopa_year=self.year,
                #     path={'query': self.context.absolute_url_path(),
                #           'depth': 2})
                # for item in items:
                #     api.content.delete(obj=item)
            elif request.path[-2::-1][0] == 'copy':
                self.action = 'copy'
            else:
                self.action = 'None'
        else:
            self.action = 'None'

    def getYear(self):
        return self.year

    def __call__(self):
        if not self.year:
            # Empty query returns default template
            self.year = str(datetime.datetime.now().year)
            return self.index()
        else:
            return self.index()
        # TODO: if copy or delete make action!

    def getItems(self):
        """ Returns all the workplans inside the planning """
        items = self.context.aq_parent.items()

        results = []
        for item in items:
            if item[1].portal_type == 'WorkPlan':
                if self.context.id == item[0]:
                    classe = 'disabled'
                else:
                    classe = 'visible'
                results.append(dict(
                    title=item[0],
                    url=item[1].absolute_url_path(),
                    classe=classe))
        return sorted(results, key=itemgetter('title'), reverse=False)

    def currentYear(self):
        """ Returns current year to show in the title """
        return ' ' + self.context.absolute_url_path().split('/')[-1:][0]

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
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity', 'Output'],
            gwopa_year=self.year,
            path={'query': folder_path,
                  'depth': 1})
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
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
                url='/'.join(item.getPhysicalPath())))
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
                url='/'.join(item.getPhysicalPath())))
        return results


