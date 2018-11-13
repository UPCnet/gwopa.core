# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _

grok.templatedir("templates")


class IOutputindicator(model.Schema):
    """  Output indicator """
    title = schema.TextLine(
        title=_(u"Output"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )


class View(grok.View):
    grok.context(IOutputindicator)
    grok.template('outputindicator_view')
