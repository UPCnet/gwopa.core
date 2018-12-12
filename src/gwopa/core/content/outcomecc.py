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


class IOutcomecc(model.Schema):
    """  OutcomeCC
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=False,
    )

    wop_program = schema.List(
        title=_(u"Capacity Items"),
        description=_(u"Improved specific capacity"),
        value_type=schema.Choice(
            source=utils.settings_capacity_changes),
        required=False,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    baseline = schema.Text(
        title=_(u"Baseline description"),
        required=True,
    )

    baseline_date = schema.Date(
        title=_(u'Date of the Baseline'),
        required=True,
        defaultFactory=todayValue
    )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutcomecc)
    grok.template('outcomecc_view')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomecc)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["description"].mode = HIDDEN_MODE
