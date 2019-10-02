# -*- coding: utf-8 -*-
from five import grok
from plone.directives import form
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema

from gwopa.core import _

import datetime

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutcomeccitem(model.Schema):
    """  OutcomeCC Values
    """
    title = schema.TextLine(
        title=_(u"Title English"),
        required=True,
    )

    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=True,
    )

    title_fr = schema.TextLine(
        title=_(u"Title French"),
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

    short_category = schema.TextLine(
        title=_(u'Short Category'),
        description=_(u'Insert the used short category to group this element'),
        required=True,
    )


@indexer(IOutcomeccitem)
def title_es(context):
    try:
        value = context.title_es.decode("utf-8")
        return value
    except:
        return context.title_es


grok.global_adapter(title_es, name='title_es')


@indexer(IOutcomeccitem)
def title_fr(context):
    try:
        value = context.title_fr.decode("utf-8")
        return value
    except:
        return context.title_fr


grok.global_adapter(title_fr, name='title_fr')


class View(grok.View):
    grok.context(IOutcomeccitem)
    grok.template('outcomeccitem_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccitem)
