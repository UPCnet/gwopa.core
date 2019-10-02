# -*- coding: utf-8 -*-
from five import grok
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema

from gwopa.core import _

import datetime

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutputdefaults(model.Schema):
    """  Output Default values
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


@indexer(IOutputdefaults)
def title_es(context):
    try:
        value = context.title_es.decode("utf-8")
        return value
    except:
        return context.title_es


grok.global_adapter(title_es, name='title_es')


@indexer(IOutputdefaults)
def title_fr(context):
    try:
        value = context.title_fr.decode("utf-8")
        return value
    except:
        return context.title_fr


grok.global_adapter(title_fr, name='title_fr')


class View(grok.View):
    grok.context(IOutputdefaults)
    grok.template('output_view')
    grok.require('zope2.View')
