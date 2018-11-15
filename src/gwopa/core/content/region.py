# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from plone.namedfile import field as namedfile
from gwopa.core import _
from gwopa.core import utils

grok.templatedir("templates")


class IRegion(model.Schema):
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


class View(grok.View):
    grok.context(IRegion)
    grok.template('region_view')
