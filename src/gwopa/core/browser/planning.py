# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
import datetime


class planningView(BrowserView):
    """ get current workplan and redirect!
    """

    index = ViewPageTemplateFile('templates/planning.pt')

    def __call__(self):
        current_year = datetime.datetime.now().year
        newid = 'awp-' + str(current_year)
        folder = api.content.find(
            portal_type='WorkPlan',
            context=self.context)
        if folder:
            for item in folder:
                if item.id == newid:
                    return self.request.response.redirect(item.getPath())
            return self.request.response.redirect(folder[0].getPath())
        else:
            return self.index()

    def getWorkplan(self):
        workplan = api.content.find(
            portal_type='WorkPlan',
            context=self.context)
        if workplan:
            return True
        else:
            return False
