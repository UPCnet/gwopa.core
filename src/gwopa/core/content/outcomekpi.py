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


class IOutcomekpi(model.Schema):
    """  OutcomeKPI
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

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    baseline = schema.TextLine(
        title=_(u"Baseline value"),
        required=True,
    )

    baseline_date = schema.Date(
        title=_(u'Baseline date'),
        required=True,
        defaultFactory=todayValue
    )

    measuring_unit = schema.Choice(
        title=_(u"Measuring Unit"),
        source=utils.settings_measuring_unit,
        required=True,
    )

    measuring_frequency = schema.Choice(
        title=_(u"Measuring Frequency"),
        source=utils.settings_measuring_frequency,
        required=True,
    )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )

    risks = schema.Text(
        title=_(u"Risks / Assumptions"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutcomekpi)
    grok.template('outcomekpi_view')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomekpi)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["description"].mode = HIDDEN_MODE
