# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from gwopa.core.utils import vocabulary_values

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


indicator_type = [
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

    # target1 = schema.TextLine(
    #     title=_(u"Target value 1"),
    #     description=_(u"TODO : Problems with inline addition..."),
    #     required=True,
    # )

    # target1_date = schema.Date(
    #     title=_(u'Target Value 1 Date'),
    #     required=True,
    #     defaultFactory=todayValue
    # )

    # target2 = schema.TextLine(
    #     title=_(u"Target value 2"),
    #     description=_(u"TODO : Problems with inline addition..."),
    #     required=True,
    # )

    # target2_date = schema.Date(
    #     title=_(u'Target Value 2 Date'),
    #     required=True,
    #     defaultFactory=todayValue
    # )

    measuring = schema.Choice(
        title=_(u"Measuring Unit"),
        required=True,
        source=vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.measuring_unit'),
    )

    frequency = schema.Choice(
        title=_(u"Measuring Frequency"),
        required=True,
        source=vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.measuring_frequency'),
    )

    # disaggregation = schema.TextLine(
    #     title=_(u"Disaggregation's"),
    #     required=True,
    # )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=True,
    )


class View(grok.View):
    grok.context(IIndicator)
    grok.template('indicator_view')
