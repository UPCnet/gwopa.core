# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.supermodel.directives import fieldset
grok.templatedir("templates")


class IMainContributing(model.Schema):
    """ Main Contributing default values. """

    fieldset('english',
             label=_(u'English'),
             fields=['title']
             )

    fieldset('spanish',
             label=_(u'Spanish'),
             fields=['title_es']
             )

    fieldset('french',
             label=_(u'French'),
             fields=['title_fr']
             )

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


class View(grok.View):
    grok.context(IMainContributing)
    grok.template('maincontributing_view')
    grok.require('zope2.View')
