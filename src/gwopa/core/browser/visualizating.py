# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api


class visualizatingView(BrowserView):
    """ Shows all the visualizating options associated to one project
    """
    __call__ = ViewPageTemplateFile('templates/visualizating.pt')
