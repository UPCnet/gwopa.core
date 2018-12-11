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

    def getItems(self):
        items = self.context.aq_parent.items()
        results = []
        for item in items:
            if item[1].portal_type == 'WorkPlan':
                if self.context.id == item[0]:
                    classe = 'disabled'
                else:
                    classe = 'visible'
                results.append(dict(
                    title=item[0].split('-')[1],
                    url=item[1].absolute_url_path(),
                    classe=classe))
        return results

    def currentYear(self):
        year = self.context.absolute_url_path().split('-')[1:][0]
        return year

    def getAreas(self):
        items = api.content.find(
            portal_type='ImprovementArea',
            context=self.context)
        results = []
        for project in items:
            item = project.getObject()
            if item.image:
                image = True
            else:
                image = False
            if item.description:
                description = item.description
            else:
                description = item.title
            results.append(dict(title=item.title,
                                url=item.absolute_url_path(),
                                image=image,
                                description=description,
                                portal_type=item.portal_type
                                ))
        return results

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
            portal_type=['Activity', 'Outcome', 'Output'],
            path={'query': '/'.join(folder_path.split('/')[:-1]),
                  'depth': 1})

        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                url=item.getPath()))
        return results

    # def indicatorsInsideInside(self, item):
    #     """ Returns objects from second level, except indicators.
    #         Because an indicator inside an indicator is not accepted.
    #     """
    #     if item['portal_type'] != 'Indicator':
    #         portal_catalog = getToolByName(self, 'portal_catalog')
    #         folder_path = item['url']
    #         items = portal_catalog.unrestrictedSearchResults(
    #             path={'query': folder_path,
    #                   'depth': 1})
    #         results = []
    #         for item in items:
    #             results.append(dict(
    #                 title=item.Title,
    #                 description=item.Description,
    #                 portal_type=item.portal_type,
    #                 url=item.getPath()))
    #         return results
