# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.namedfile import field

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class ILogframe(model.Schema):
    """  Log Frame """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    file = field.NamedFile(
        title=_(u"File"),
        description=_(u"Upload a file"),
        required=False,
    )


class View(grok.View):
    grok.context(ILogframe)
    grok.template('logframe_view')
