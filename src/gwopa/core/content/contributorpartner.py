# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.autoform import directives
from plone.directives import form
from gwopa.core import utils

grok.templatedir("templates")


class IContribPartner(model.Schema):
    """  Partner contributor
    """
    title = schema.TextLine(
        title=_(u"Name"),
        required=True,
    )

    incash = schema.Decimal(
        title=_(u'In-cash'),
        required=False,
    )

    directives.mode(currency_incash='display')
    currency_incash = schema.TextLine(
        title=_(u""),
    )

    inkind = schema.Decimal(
        title=_(u'In-kind'),
        required=False,
    )

    directives.mode(currency_inkind='display')
    currency_inkind = schema.TextLine(
        title=_(u""),
    )


@form.default_value(field=IContribPartner['currency_incash'])
@form.default_value(field=IContribPartner['currency_inkind'])
def defaultCurrency(data):
    return utils.project_currency(data)


class View(grok.View):
    grok.context(IContribPartner)
    grok.template('contributor_view')
    grok.require('zope2.View')
