# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class ITargetvalue(model.Schema):
    """  Project type
    """
    targetvalue = schema.TextLine(
        title=_(u"Target Value title"),
        required=True,
    )

    targetvalue_date = schema.Date(
        title=_(u'Target Value Date'),
        required=True,
        defaultFactory=todayValue
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )


class View(grok.View):
    grok.context(ITargetvalue)
    grok.template('targetvalue_view')