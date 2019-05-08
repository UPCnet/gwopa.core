# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutcomedefaults(model.Schema):
    """  Outcome Default values
    """

    number = schema.TextLine(
        title=_(u"KPI Number"),
        required=True,
    )

    title = schema.TextLine(
        title=_(u"Title English"),
        required=True,
    )

    unit = schema.TextLine(
        title=_(u"Unit"),
        required=True,
    )

    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=False,
    )

    title_fr = schema.TextLine(
        title=_(u"Title French"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutcomedefaults)
    grok.template('output_view')  # no additional view needed
    grok.require('zope2.View')
