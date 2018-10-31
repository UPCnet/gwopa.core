# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

grok.templatedir("templates")


def todayValue():
    return datetime.date.today() - datetime.timedelta(1)


indicator_kind = [
    u"Goal",
    u"Objective",
    u"Outcome",
    u"Output",
]

indicator_type = [
    u"None",
    u"Qualitative",
    u"Quantitative",
]


class IIndicator(model.Schema):
    """  indicator """

    def get_vocabulary(values):
        return SimpleVocabulary([
            SimpleTerm(title=_(value), value=value, token=token)
            for token, value in enumerate(values)])

    title = schema.TextLine(
        title=_(u"Indicator title"),
        required=True,
    )

    description = schema.TextLine(
        title=_(u"Describe Indicator"),
        required=True,
    )

    indicator_kind = schema.Choice(
        title=_(u"Indicate which results chain component it is informing"),
        vocabulary=get_vocabulary(indicator_kind),
        required=True,
    )

    indicator_type = schema.Choice(
        title=_(u"Indicator type"),
        vocabulary=get_vocabulary(indicator_type),
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
