# -*- coding: utf-8 -*-
import datetime
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core.utils import vocabulary_values
from gwopa.core import _

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutcomeindicator(model.Schema):
    """  Outcome indicator
    """
    title = schema.TextLine(
        title=_(u"Outcome"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
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
    grok.context(IOutcomeindicator)
    grok.template('outcomeindicator_view')
