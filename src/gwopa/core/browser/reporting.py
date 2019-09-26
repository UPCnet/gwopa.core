# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api


class reportingView(BrowserView):
    """ Shows all the reporting options associated to one project
    """
    __call__ = ViewPageTemplateFile('templates/reporting.pt')
