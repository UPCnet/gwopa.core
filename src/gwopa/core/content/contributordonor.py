# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _

grok.templatedir("templates")


class IContribDonor(model.Schema):
    """  Donor contributor
    """
    title = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )

    incash = schema.Float(
        title=_(u'In-cash'),
        required=False,
    )

    inkind = schema.Float(
        title=_(u'In-kind'),
        required=False,
    )


class View(grok.View):
    grok.context(IContribDonor)
    grok.template('contributor_view')
    grok.require('zope2.View')
