# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _

grok.templatedir("templates")


class IImprovementArea(model.Schema):
    """ areat type
    """
    title = schema.TextLine(
        title=_(u"Improvement Area"),
        description=_(u"An improvement area used on the Site"),
        required=False,
    )


class View(grok.View):
    grok.context(IImprovementArea)
    grok.template('improvementarea_view')
