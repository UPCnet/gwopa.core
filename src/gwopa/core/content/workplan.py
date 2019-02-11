# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
from plone import api

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IWorkplan(model.Schema):
    """  Log Frame """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )


class View(grok.View):
    grok.context(IWorkplan)
    grok.template('workplan_view')

    def getItems(self):
        """ Returns all the worklans inside the planning """
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
        """ Returns all the Activitys of this Planning year """
        items = api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context.aq_parent)
        results = []
        for project in items:
            item = project.getObject()
            results.append(dict(title=item.title,
                                url='/'.join(item.getPhysicalPath()),
                                description=item.description,
                                portal_type=item.portal_type
                                ))
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

    def indicatorsInside(self, item):
        """ returns objects from first level (elemnents inside ImprovementArea) """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity', 'Output'],
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
