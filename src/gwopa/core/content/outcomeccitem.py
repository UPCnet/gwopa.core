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


class IOutcomeccitem(model.Schema):
    """  OutcomeCC Values
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    icon = schema.TextLine(
        title=_(u"Icon"),
        description=_(u"Insert the Font Awesome icon to describe this Outcome. IE: fa-globe"),
        required=True,
    )

    category = schema.TextLine(
        title=_(u'Category'),
        description=_(u'Insert the used category to group this element'),
        required=True,
    )


class View(grok.View):
    grok.context(IOutcomeccitem)
    grok.template('outcomeccitem_view')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccitem)
