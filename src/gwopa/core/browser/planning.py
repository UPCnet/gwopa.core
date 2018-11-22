# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api


class planningView(BrowserView):
    """ View all the indicators associated to the project
    """
    __call__ = ViewPageTemplateFile('templates/planning.pt')

    def getTitle(self):
        return self.context.Title()

    def getLogFrame(self):
        logframes = api.content.find(
            portal_type='LogFrame',
            context=self.context)

        if not logframes:
            return False
        else:
            results = []
            for item in logframes:
                results.append(dict(
                    title=item.Title,
                    description=item.Description,
                    portal_type=item.portal_type,
                    url=item.getPath()))
            return results

    def getWorkPlan(self):
        workplan = api.content.find(
            portal_type='WorkPlan',
            context=self.context['indicators'])

        if not workplan:
            return False
        else:
            results = []
            for item in workplan:
                results.append(dict(
                    title=item.Title,
                    description=item.Description,
                    portal_type=item.portal_type,
                    url=item.getPath()))
            return results
