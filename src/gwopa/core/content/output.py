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


def endDefaultValue():
    return datetime.datetime.today() + datetime.timedelta(10)


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

    initial_situation = schema.Text(
        title=_(u'Initial situation description'),
        required=False,
        missing_value=u'',
    )

    end = schema.Datetime(
        title=_(u'Completion time'),
        required=True,
        defaultFactory=endDefaultValue
    )

    target = schema.Text(
        title=_(u"Measurable Target"),
        required=True,
    )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )

    risks = schema.Text(
        title=_(u"Risks / Assumptions"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutput)
    grok.template('output_view')
