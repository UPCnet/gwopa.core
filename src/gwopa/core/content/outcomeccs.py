# -*- coding: utf-8 -*-
import datetime
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.directives import form

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutcomeccs(model.Schema):
    """  OutcomeCCS
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )


class View(grok.View):
    grok.context(IOutcomeccs)
    grok.template('outcomeccs_view')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccs)
