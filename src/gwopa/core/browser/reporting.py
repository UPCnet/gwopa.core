# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class reportingView(BrowserView):
    """ Shows all the reporting options associated to one project
    """
    __call__ = ViewPageTemplateFile('templates/reporting.pt')

    def projectTitle(self):
        return self.context.title

    def getReports(self):
        portal_catalog = getToolByName(self, 'portal_catalog')
        reports = portal_catalog.unrestrictedSearchResults(
            portal_type=['File'],
            path={'query': self.context.absolute_url_path() + '/reports'},
            sort_on='created',
            sort_order='descending'
        )
        return reports

    def projectURL(self):
        return self.context.absolute_url()
