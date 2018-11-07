# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api


class listIndicators(BrowserView):
    """ View that list all members of the organ de govern"""
    __call__ = ViewPageTemplateFile('templates/indicators.pt')

    def getTitle(self):
        return self.context.Title()

    def goalsList(self):
        items = api.content.find(portal_type='GoalIndicator')
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                url=item.getPath()))
        return results

    def indicatorsInside(self, item):
        items = api.content.find(portal_type='GoalIndicator', path=item.getPath())
        results = []
        for item in items:
            results.append(dict(
                title=item.Title,
                description=item.Description,
                url=item.getPath()))
        return results
