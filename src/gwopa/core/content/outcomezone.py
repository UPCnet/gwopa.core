# -*- coding: utf-8 -*-
import datetime
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import utils
from gwopa.core import _
from plone.directives import form
from plone.autoform import directives
from plone.app.z3cform.widget import SelectWidget
from z3c.form.interfaces import DISPLAY_MODE

grok.templatedir("templates")


def todayValue():
    """ Today. """
    return datetime.datetime.today()


class IOutcomezone(model.Schema):
    """  OutcomeZONE. """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    zone = schema.TextLine(
        title=_(u'Zone'),
        required=False,
    )

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    baseline = schema.TextLine(
        title=_(u"Baseline value"),
        required=True,
    )

    baseline_date = schema.Datetime(
        title=_(u'Baseline date'),
        required=True,
        defaultFactory=todayValue
    )

    measuring_unit = schema.Choice(
        title=_(u"Measuring unit"),
        source=utils.settings_measuring_unit,
        required=True,
    )

    # measuring_frequency = schema.Choice(
    #     title=_(u"Monitoring and reporting frequency"),
    #     source=utils.settings_measuring_frequency,
    #     required=True,
    # )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )

    risks = schema.Text(
        title=_(u"Risks and Assumptions at project level!"),
        required=False,
    )


class View(grok.View):
    grok.context(IOutcomezone)
    grok.template('outcomezone_view')
    grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(IOutcomezone)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = DISPLAY_MODE
        #self.widgets["measuring_frequency"].mode = DISPLAY_MODE
