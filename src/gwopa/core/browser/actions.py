# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import alsoProvides
from plone.protect.interfaces import IDisableCSRFProtection
import datetime
from operator import itemgetter


class AddWorkPlan(BrowserView):
    """ Create current WorkPlan folder
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        current_year = datetime.datetime.now().year
        api.content.create(
            type='WorkPlan',
            id='awp-' + str(current_year),
            container=self.context)

        return self.request.response.redirect(self.context.absolute_url_path() + '/planning')


class CopyWorkPlan(BrowserView):
    """ Copy WorkPlan folder
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        items = api.content.find(
            portal_type='WorkPlan',
            context=self.context.aq_parent)
        plans = sorted(items, key=itemgetter('id'), reverse=True)
        newyear = int(plans[0].id.split('-')[1]) + 1
        api.content.copy(source=plans[0].getObject(), target=self.context.aq_parent, id='awp-' + str(newyear))
        return self.request.response.redirect(self.context.aq_parent.absolute_url_path() + '/planning')


class DeleteWorkPlan(BrowserView):
    """ Delete WorkPlan folder
    """
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        api.content.delete(obj=self.context)
        return self.request.response.redirect(self.context.aq_parent.absolute_url_path())
