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

    description = schema.TextLine(
        title=_(u"Describe Indicator"),
        required=True,
    )

    indicator_kind = schema.TextLine(
        title=_(u"Indicate which results chain component it is informing"),
        required=True,
    )

    indicator_type = schema.TextLine(
        title=_(u"Indicator type"),
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

    target1 = schema.TextLine(
        title=_(u"Target value 1"),
        description=_(u"TODO : Problems with inline addition..."),
        required=True,
    )

    target1_date = schema.Date(
        title=_(u'Target Value 1 Date'),
        required=True,
        defaultFactory=todayValue
    )

    target2 = schema.TextLine(
        title=_(u"Target value 2"),
        description=_(u"TODO : Problems with inline addition..."),
        required=True,
    )

    target2_date = schema.Date(
        title=_(u'Target Value 2 Date'),
        required=True,
        defaultFactory=todayValue
    )

    measuring = schema.TextLine(
        title=_(u"Measuring Unit"),
        required=True,
    )

    frequency = schema.TextLine(
        title=_(u"Measuring Frequency"),
        required=True,
    )

    disaggregation = schema.TextLine(
        title=_(u"Disaggregation's"),
        required=True,
    )


class View(grok.View):
    grok.context(IIndicator)
    grok.template('indicator_view')
