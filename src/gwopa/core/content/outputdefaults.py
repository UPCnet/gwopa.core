# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.supermodel.directives import fieldset
grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutputdefaults(model.Schema):
    """  Output Default values
    """

    fieldset('English',
             label=_(u'Project'),
             fields=['title', 'unit']
             )

    fieldset('Spanish',
             label=_(u'Image'),
             fields=['title_es', 'unit_es']
             )

    fieldset('French',
             label=_(u'Image'),
             fields=['title_fr', 'unit_fr']
             )

    title = schema.TextLine(
        title=_(u"Title English"),
        required=True,
    )

    unit = schema.TextLine(
        title=_(u"Measuring unit EN"),
        required=True,
    )

    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=False,
    )

    unit_es = schema.TextLine(
        title=_(u"Measuring unit ES"),
        required=True,
    )

    title_fr = schema.TextLine(
        title=_(u"Title French"),
        required=False,
    )

    unit_fr = schema.TextLine(
        title=_(u"Measuring unit FR"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutputdefaults)
    grok.template('output_view')
    grok.require('zope2.View')
