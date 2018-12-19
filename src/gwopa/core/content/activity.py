# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from zope.interface import Invalid
from zope.interface import invariant
from gwopa.core import utils
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives


grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


def startDefaultValue():
    return datetime.datetime.today() + datetime.timedelta(7)


def endDefaultValue():
    return datetime.datetime.today() + datetime.timedelta(10)


class IActivity(model.Schema):
    """  Activity """

    title = schema.TextLine(
        title=_(u"Name"),
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

    start = schema.Datetime(
        title=_(u'Starting time'),
        required=True,
        defaultFactory=startDefaultValue
    )

    end = schema.Datetime(
        title=_(u'Completion time'),
        required=True,
        defaultFactory=endDefaultValue
    )

    inputs = schema.Text(
        title=_(u'Related inputs'),
        required=False,
        missing_value=u'',
    )

    bidget = schema.Text(
        title=_(u'Assigned budget'),
        required=False,
        missing_value=u'',
    )

    milestones = schema.Text(
        title=_(u'Milestones'),
        required=False,
        missing_value=u'',
    )

    directives.widget('outputs', SelectWidget)
    outputs = schema.List(
        title=_(u"Related outputs"),
        value_type=schema.Choice(
            source=utils.outputs),
        required=False,
    )

    members = schema.Choice(
        title=_(u"Members"),
        description=_(u"Members of this activity"),
        required=False,
        vocabulary=u'plone.app.vocabularies.Users',
    )

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(u"End date must be after start date.")


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
