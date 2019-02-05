# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
import datetime
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides


class planningView(BrowserView):
    """ get current workplan and redirect!
    """

    def __call__(self):
        current_year = datetime.datetime.now().year
        newid = str(current_year)
        folder = api.content.find(
            portal_type='WorkPlan',
            context=self.context)
        if folder:
            for item in folder:
                if item.id == newid:
                    return self.request.response.redirect(item.getObject().absolute_url_path())
            alsoProvides(self.request, IDisableCSRFProtection)
            newplan = api.content.create(
                type='WorkPlan',
                id=str(current_year),
                container=self.context)
            return self.request.response.redirect(newplan.absolute_url_path())
        else:
            alsoProvides(self.request, IDisableCSRFProtection)
            newplan = api.content.create(
                type='WorkPlan',
                id=str(current_year),
                container=self.context)
            return self.request.response.redirect(newplan.absolute_url_path())

    def getWorkplan(self):
        workplan = api.content.find(
            portal_type='WorkPlan',
            context=self.context)
        if workplan:
            return True
        else:
            return False
