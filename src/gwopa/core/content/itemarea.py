# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.directives import form

grok.templatedir("templates")


class IItemArea(model.Schema):
    """  Improvement Area Values
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )


class View(grok.View):
    grok.context(IItemArea)
    grok.template('itemarea_view')


class Edit(form.SchemaEditForm):
    grok.context(IItemArea)
