# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from gwopa.core import utils
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

    # measuring_unit = schema.Choice(
    #     title=_(u"Measuring unit"),
    #     source=utils.settings_measuring_unit,
    #     required=True,
    # )


class View(grok.View):
    grok.context(IOutputdefaults)
    grok.template('output_view')
    grok.require('zope2.View')
