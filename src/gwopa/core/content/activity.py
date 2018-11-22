# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IActivity(model.Schema):
    """  Activity """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    milestones = schema.Text(
        title=_(u'Milestones'),
        required=False,
        missing_value=u'',
    )

    members = schema.Choice(
        title=_(u"Members"),
        description=_(u"Members of this activity"),
        required=False,
        vocabulary=u'plone.app.vocabularies.Users',
    )


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
