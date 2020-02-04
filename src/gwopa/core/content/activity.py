# -*- coding: utf-8 -*-
from five import grok
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from plone.directives import form
from plone.supermodel import model
from zope import schema
from zope.globalrequest import getRequest
from zope.interface import Invalid
from zope.interface import invariant

from gwopa.core import _
from gwopa.core.utils import project_currency

import datetime

grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The starting date must be before the completion date")


def todayValue():
    return datetime.datetime.today()


current_year = datetime.date.today().year


def checkDate(value):
    if value:
        req = getRequest()
        context = req.PARENTS[0]
        start_project = context.aq_parent.startactual.toordinal()
        end_project = context.aq_parent.completionactual.toordinal()
        date = value.date().toordinal()
        if not (date <= end_project and date >= start_project):
            raise Invalid(_(u'This date must be between the dates of the project.'))
    return True


class IDate(schema.Date):
    text = schema.Text(
        title=_(u"Target Value Year"),
    )


class IActivity(model.Schema):
    """  Activity """

    title = schema.TextLine(
        title=_(u"Numeration - Title"),
        description=_(u"(e.g. 1 - Training of staff in NRW reduction approachesZ)"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    initial_situation = schema.Text(
        title=_(u'Description of initial situation'),
        required=False,
        missing_value=u'',
    )

    directives.mode(project_dates='display')
    project_dates = schema.Text(
        title=_(u''),
    )

    start = schema.Datetime(
        title=_(u'Starting date'),
        required=True,
        constraint=checkDate
    )

    end = schema.Datetime(
        title=_(u'Completion date'),
        required=True,
        constraint=checkDate
    )

    directives.mode(explain_budget='display')
    explain_budget = schema.Text(
        title=_(u'As it is common practice for utilities involved in WOPs to manage the financial tracking in-house, expenditure is not tracked within the tool. We do however provide a section within the reporting feature to document basic expenditures.'),
    )

    budget = schema.TextLine(
        title=_(u'Assigned budget'),
        required=False,
    )

    directives.mode(currency='display')
    currency = schema.TextLine(
        title=_(u'Project Currency'),
    )

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )

    # risks = schema.Text(
    #     title=_(u"Risks / Assumptions"),
    #     required=False,
    # )

    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd(_(u"The starting date must be before the completion date."))


@form.default_value(field=IActivity['currency'])
def projectCurrency(data):
    return project_currency(data.context.aq_parent)


@form.default_value(field=IActivity['project_dates'])
def projectDates(data):
    return _(u"The dates must be between the limits of this Project. Start: ") + str(data.context.aq_parent.startactual) + _u(" End: ") + str(data.context.aq_parent.completionactual)


# @form.default_value(field=IActivity['explain_budget'])
# def explainBudget(data):
#     return _u("As it is common practice for utilities involved in WOPs to manage the financial tracking in-house, expenditure is not tracked within the tool. We do however provide a section within the reporting feature to document basic expenditures.")


class Edit(form.SchemaEditForm):
    grok.context(IActivity)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
    grok.require('zope2.View')
