# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from zope.interface import Invalid
from zope.interface import invariant
from gwopa.core import _
import datetime

grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def todayValue(context):
    return datetime.date.today() - datetime.timedelta(1)


class IOutputindicator(model.Schema):
    """  Output indicator """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    start = schema.Date(
        title=_(u'Start date'),
        description=_(u'Date when the indicator begins.'),
        required=True,
        defaultFactory=todayValue
    )

    end = schema.Date(
        title=_(u'End date'),
        description=_(u'Date when the indicator ends.'),
        required=True,
        defaultFactory=todayValue
    )

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(u"End date must be after start date.")


class View(grok.View):
    grok.context(IOutputindicator)
    grok.template('outputindicator_view')
