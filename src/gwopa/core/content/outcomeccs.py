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

    degree_changes = schema.Text(
        title=_(u"Select what best represents the perceived degree of change with respect to the last reporting period"),
        required=False,
    )

    contributed_project = schema.Text(
        title=_(u"Select how much has contributed to the project"),
        required=False,
    )

    contributing_factors = schema.Text(
        title=_(u"Select the contributing factors to the perceived change"),
        required=False,
    )

    obstacles = schema.Text(
        title=_(u"Select the main obstacles"),
        required=False,
    )

    limiting_factors = schema.Text(
        title=_(u"Select the limiting factors to the perceived change"),
        required=False,
    )

    consensus = schema.Text(
        title=_(u"Cnsensus"),
        required=False,
    )

    explain = schema.Text(
        title=_(u"Explain"),
        required=False,
    )



class View(grok.View):
    grok.context(IOutcomeccs)
    grok.template('outcomeccs_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccs)
