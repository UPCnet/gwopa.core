# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from plone.namedfile import field as namedfile
from plone import api
from gwopa.core import _
from gwopa.core import utils

grok.templatedir("templates")


class IPlatform(model.Schema):
    """  Project type
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
        required=False,
    )

    country = schema.List(
        title=_(u"Country"),
        description=_(u"Choose countries from list that represents this country."),
        value_type=schema.Choice(
            source=utils.countries),
        required=True,
    )

    region = schema.List(
        title=_(u"Region"),
        description=_(u"Choose region based on selected country."),
        value_type=schema.Choice(
            source=utils.countries),
        required=True,
    )


class View(grok.View):
    grok.context(IPlatform)
    grok.template('platform_view')
    grok.require('zope2.View')

    def listMembers(self):
        """ Returns users registerd on this Region """
        members = api.user.get_users()
        results = []

        for item in members:
            value = getattr(item, 'wop_platform', None)
            if value == self.context.Title():
                results += [{
                    'id': item.id,
                    'country': item.getProperty('country'),
                }]
        return results
