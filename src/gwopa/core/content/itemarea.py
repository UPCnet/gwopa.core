# -*- coding: utf-8 -*-
from five import grok
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile import field as namedfile
from plone.supermodel import model
from zope import schema

from gwopa.core import _

grok.templatedir("templates")


class IItemArea(model.Schema):
    """  Improvement Area Values
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

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Image'),
        description=_(u"Image used to describe the Working Area"),
        required=False,
    )


@indexer(IItemArea)
def title_es(context):
    try:
        value = context.title_es.decode("utf-8")
        return value
    except:
        return context.title_es


grok.global_adapter(title_es, name='title_es')


@indexer(IItemArea)
def title_fr(context):
    try:
        value = context.title_fr.decode("utf-8")
        return value
    except:
        return context.title_fr


grok.global_adapter(title_fr, name='title_fr')


class View(grok.View):
    grok.context(IItemArea)
    grok.template('itemarea_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IItemArea)
