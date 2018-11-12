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


class IIndicator(model.Schema):
    """  indicator """

    def get_vocabulary(values):
        return SimpleVocabulary([
            SimpleTerm(title=_(value), value=value, token=token)
            for token, value in enumerate(values)])

    title = schema.TextLine(
        title=_(u"Indicator"),
        required=True,
    )

    description = schema.TextLine(
        title=_(u"Describe Indicator"),
        required=False,
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

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )


class View(grok.View):
    grok.context(IIndicator)
    grok.template('indicator_view')
