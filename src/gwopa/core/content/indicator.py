# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime

grok.templatedir("templates")


def todayValue():
    return datetime.date.today() - datetime.timedelta(1)


class IIndicator(model.Schema):
    """  Quantitative indicator """
    title = schema.TextLine(
        title=_(u"Indicator title"),
        required=True,
    )

    baseline = schema.Int(
        title=_(u"Baseline value"),
        required=True,
    )

    baseline_date = schema.Date(
        title=_(u'Baseline Date'),
        required=True,
        defaultFactory=todayValue
    )

    target = schema.TextLine(
        title=_(u"Target value"),
        description=_(u"TODO : Problems with inline addition..."),
        required=True,
    )

    measuring = schema.TextLine(
        title=_(u"Measuring Unit"),
        required=True,
    )

    frequency = schema.TextLine(
        title=_(u"Frequency"),
        required=True,
    )

    primary_data = schema.TextLine(
        title=_(u"Primary Source of Data"),
        required=True,
    )


class View(grok.View):
    grok.context(IIndicator)
    grok.template('indicator_view')
