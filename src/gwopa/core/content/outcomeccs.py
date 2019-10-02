# -*- coding: utf-8 -*-
from five import grok
from plone.autoform import directives
from plone.directives import form
from plone.indexer import indexer
from plone.supermodel import model
from zope import schema

from gwopa.core import _

grok.templatedir("templates")


class IOutcomeccs(model.Schema):
    """  OutcomeCCS
    """

    directives.mode(title='hidden')
    title = schema.TextLine(
        title=_(u"Title English"),
        required=True,
    )

    directives.mode(title_es='hidden')
    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=True,
    )

    directives.mode(title_fr='hidden')
    title_fr = schema.TextLine(
        title=_(u"Title French"),
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

    consensus = schema.Text(
        title=_(u"Consensus"),
        required=False,
    )

    explain = schema.Text(
        title=_(u"Explain"),
        required=False,
    )


@indexer(IOutcomeccs)
def title_es(context):
    try:
        value = context.title_es.decode("utf-8")
        return value
    except:
        return context.title_es


grok.global_adapter(title_es, name='title_es')


@indexer(IOutcomeccs)
def title_fr(context):
    try:
        value = context.title_fr.decode("utf-8")
        return value
    except:
        return context.title_fr


grok.global_adapter(title_fr, name='title_fr')


class View(grok.View):
    grok.context(IOutcomeccs)
    grok.template('outcomeccs_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccs)
