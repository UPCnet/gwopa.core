# -*- coding: utf-8 -*-
import datetime
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import utils
from gwopa.core import _
from z3c.form.interfaces import HIDDEN_MODE  # INPUT_MODE, DISPLAY_MODE
from plone.directives import form

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutcomeccvalues(model.Schema):
    """  OutcomeCC Values
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    icon = schema.TextLine(
        title=_(u"Icon"),
        required=True,
    )

    category = schema.Text(
        title=_(u'Category'),
        required=False,
        missing_value=u'',
    )

    baseline = schema.Text(
        title=_(u"Baseline description"),
        required=True,
    )

    perceived_changes = schema.Text(
        title=_(u'Describe perceived changes in the selected dimension'),
    )

    degree_changes = schema.Text(
        title=_(u"Select what best represents the perceived degree of change with respect to the last reporting period"),
    )

    contributing_factors = schema.Text(
        title=_(u"Select the contributing factors to the perceived change")
    )

    describe_factors = schema.Text(
        title=_(u"Describe the contributing factors to the perceived changes")
    )

    limiting_factors = schema.Text(
        title=_(u"Select the limiting factors to the perceived change")
    )

    describe_factors = schema.Text(
        title=_(u"Describe the limiting factors to the perceived changes")
    )

    means_of_verification = schema.Text(
        title=_(u"Means of verification used to assess capacity change in this dimension")
    )

    participation = schema.Text(
        title=_(u"Inform participation in the assessment")
    )


class View(grok.View):
    grok.context(IOutcomeccvalues)
    grok.template('outcomeccvalues_view')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomeccvalues)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["description"].mode = HIDDEN_MODE
