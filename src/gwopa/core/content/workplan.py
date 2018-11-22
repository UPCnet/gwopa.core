# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
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

    def projectUrl(self):
        return self.context.aq_parent.aq_parent.absolute_url()

    def listActivities(self):
        items = api.content.find(
            portal_type='Activity',
            context=self.context)
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                url=item.getPath()))
        return results

    def goalsList(self):
        items = api.content.find(
            portal_type='Goal',
            context=self.context)
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
