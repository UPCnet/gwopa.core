# -*- coding: utf-8 -*-
from five import grok
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema

from gwopa.core import _

grok.templatedir("templates")


class IMainContributing(model.Schema):
    """ Main Contributing default values. """

    title = schema.TextLine(
        title=_(u"Title English"),
        required=True,
    )

    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=False,
    )

    title_fr = schema.TextLine(
        title=_(u"Title French"),
        required=False,
    )


@indexer(IMainContributing)
def title_es(context):
    try:
        value = context.title_es.decode("utf-8")
        return value
    except:
        return context.title_es


grok.global_adapter(title_es, name='title_es')


@indexer(IMainContributing)
def title_fr(context):
    try:
        value = context.title_fr.decode("utf-8")
        return value
    except:
        return context.title_fr


grok.global_adapter(title_fr, name='title_fr')


class View(grok.View):
    grok.context(IMainContributing)
    grok.template('maincontributing_view')
    grok.require('zope2.View')
