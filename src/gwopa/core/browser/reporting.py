# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from operator import itemgetter

from gwopa.core import _


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
            path={'query': '/'.join(self.context.getPhysicalPath()) + '/reports'},
            sort_on='created',
            sort_order='descending'
        )
        return reports

    def projectURL(self):
        return self.context.absolute_url()

    def getItems(self):
        """ Returns all the project years of the planning """
        items = len(self.context.gwopa_year_phases)
        results = []
        total = 0

        while total != items:
            if total == 0:
                url = self.context.absolute_url_path() + '/reportPreview/'
            else:
                url = self.context.absolute_url_path() + '/reportPreview/' + str(total + 1)
            results.append(dict(
                title=_(u"Project year"),
                year=str(total + 1),
                url=url,
                alt=_(u"Show report preview of year ") + str(total + 1)))
            total = total + 1

        return sorted(results, key=itemgetter('title'), reverse=False)
