# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from gwopa.core import utils


grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutput(model.Schema):
    """  Output
    """
    title = schema.TextLine(
        title=_(u"Title"),
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
        source=utils.settings_measuring_unit,
    )

    frequency = schema.Choice(
        title=_(u"Measuring Frequency"),
        required=True,
        source=utils.settings_measuring_frequency,
    )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutput)
    grok.template('output_view')