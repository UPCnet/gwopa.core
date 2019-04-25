# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.directives import form
from z3c.form.interfaces import IAddForm, IEditForm
from plone.autoform import directives
from plone.app.z3cform.widget import SelectWidget
from gwopa.core import utils
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE, INPUT_MODE

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutput(model.Schema):
    """  Output
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    initial_situation = schema.Text(
        title=_(u'Baseline description'),
        required=False,
        missing_value=u'',
    )

    end = schema.Date(
        title=_(u'Completion date'),
        required=True,
        defaultFactory=todayValue
    )

    measuring_unit = schema.Choice(
        title=_(u"Measuring unit"),
        source=utils.settings_measuring_unit,
        required=True,
    )

    measuring_frequency = schema.Choice(
        title=_(u"Measuring frequency"),
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

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )


class Edit(form.SchemaEditForm):
    grok.context(IOutput)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = DISPLAY_MODE


class View(grok.View):
    grok.context(IOutput)
    grok.template('output_view')
    grok.require('zope2.View')
