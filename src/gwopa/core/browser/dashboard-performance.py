# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from operator import itemgetter
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from gwopa.core.utils import getTranslatedOutcomesFromTitle


@implementer(IPublishTraverse)
class dashboardPerformanceView(BrowserView):
    """ Visualization View """

    index = ViewPageTemplateFile("templates/dash-performance.pt")

    def __call__(self):
        return self.index()

    def projectTitle(self):
        return self.context.title

    def getItems(self):
        """ Returns all the KPIs from project  """
        items = api.content.find(
            portal_type=['OutcomeZONE'],
            context=self.context)

        results = []
        if len(items) != 0:
            for (i, project) in enumerate(items):
                item = project.getObject()

                results.append(dict(title=getTranslatedOutcomesFromTitle(item.title),
                                    url='/'.join(item.getPhysicalPath()),
                                    id=item.id,
                                    pos=i,
                                    ))
            return sorted(results, key=itemgetter('title'), reverse=False)
        else:
            return None
