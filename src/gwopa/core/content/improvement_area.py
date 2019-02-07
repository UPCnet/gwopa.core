# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.namedfile import field as namedfile
from plone import api
from Products.CMFCore.utils import getToolByName

grok.templatedir("templates")


class IImprovementArea(model.Schema):
    """  Improvement Area type
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Image'),
        description=_(u"Image used to describe the Area. If no file chosen, a defult one will be used."),
        required=False,
    )


class View(grok.View):
    grok.context(IImprovementArea)
    grok.template('improvementarea_view')

    def getFiles(self):
        """ Return files of the Area """
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['File'],
            path={'query': self.context.absolute_url_path() + '/files',
                  'depth': 1})
        results = []
        lang = api.portal.get_current_language()
        if lang == 'es':
            FORMAT_DATE = '%d/%m/%Y'
        else:
            FORMAT_DATE = '%m/%d/%Y'
        for item in items:
            results += [{'title': item.Title,
                         'portal_type': item.portal_type,
                         'url': item.getURL(),
                         'date': item.modification_date.strftime(FORMAT_DATE)
                         }]
        return results

    def getTopics(self):
        """ Return files of the Area """
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Topic'],
            path={'query': self.context.absolute_url_path() + '/topics',
                  'depth': 1})
        results = []
        for item in items:
            results += [{'title': item.Title,
                         'url': item.getURL(),
                         }]
        return results

    def getMembers(self):
        """ Returns Site Members """
        members = api.user.get_users()
        results = []

        for item in members:
            results += [{'id': item.id,
                         'country': item.getProperty('country')
                         }]
        return results
