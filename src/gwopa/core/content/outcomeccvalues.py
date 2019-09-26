# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import utils
from gwopa.core import _
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE  # INPUT_MODE
from plone.directives import form
from plone import api

grok.templatedir("templates")


class IOutcomeccvalues(model.Schema):
    """  OutcomeCC Values
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    wop_program = schema.Choice(
        title=_(u"Capacity Items"),
        description=_(u"Improved specific capacity"),
        source=utils.settings_capacity_changes,
        required=True,
    )

    baseline = schema.Text(
        title=_(u"Baseline description"),
        required=False,
    )

    perceived_changes = schema.Text(
        title=_(u'Describe perceived changes in the selected dimension'),
        required=False,
    )

    degree_changes = schema.Text(
        title=_(u"Select what best represents the perceived degree of change with respect to the last reporting period"),
        required=False,
    )

    contributing_factors = schema.Text(
        title=_(u"Select the contributing factors to the perceived change"),
        required=False,
    )

    describe_factors = schema.Text(
        title=_(u"Describe the contributing factors to the perceived changes"),
        required=False,
    )

    limiting_factors = schema.Text(
        title=_(u"Select the limiting factors to the perceived change"),
        required=False,
    )

    describe_factors = schema.Text(
        title=_(u"Describe the limiting factors to the perceived changes"),
        required=False,
    )

    means_of_verification = schema.Text(
        title=_(u"Means of verification used to assess capacity change in this dimension"),
        required=False,
    )

    participation = schema.Text(
        title=_(u"Inform participation in the assessment"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutcomeccvalues)
    grok.template('outcomeccvalues_view')
    grok.require('zope2.View')

    def getData(self):
        results = []
        value = self.context.wop_program
        result = api.content.find(portal_type="OutcomeCCItem", Title=value)[0]
        results.append(dict(
            icon=result.getObject().icon,
            title=result.Title,
            category=result.getObject().category,
        ))
        return results[0]


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccvalues)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["wop_program"].mode = DISPLAY_MODE
