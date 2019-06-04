# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.directives import form
from plone.autoform import directives

grok.templatedir("templates")


class IOutcomeccs(model.Schema):
    """  OutcomeCCS
    """

    directives.mode(title='hidden')
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    baseline = schema.TextLine(
        title=_(u"Baseline"),
        required=True,
    )

    baseline_date = schema.Date(
        title=_(u'Baseline date'),
        required=True
    )

    objective = schema.Text(
        title=_(u"Objective"),
        required=False,
    )

    objective_date = schema.Date(
        title=_(u"Objective date"),
        required=False
    )


class View(grok.View):
    grok.context(IOutcomeccs)
    grok.template('outcomeccs_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccs)
