# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.directives import form
from plone.namedfile import field as namedfile


grok.templatedir("templates")


class IItemArea(model.Schema):
    """  Improvement Area Values
    """
    title = schema.TextLine(
        title=_(u"Title"),
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


class View(grok.View):
    grok.context(IItemArea)
    grok.template('itemarea_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IItemArea)
