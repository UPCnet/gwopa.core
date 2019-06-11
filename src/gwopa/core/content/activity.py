# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from plone.directives import form
from zope.interface import invariant, Invalid
from zope.globalrequest import getRequest


grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"The starting date must be before the completion date")


# class Outofproject(Invalid):
#     __doc__ = _(u"This date must be between the dates of the project.")


def todayValue():
    return datetime.date.today()


current_year = datetime.date.today().year


def checkDate(value):
    if value:
        req = getRequest()
        context = req.PARENTS[0]
        start_project = context.aq_parent.startactual.toordinal()
        end_project = context.aq_parent.completionactual.toordinal()
        date = value.toordinal()
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
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    initial_situation = schema.Text(
        title=_(u'Initial situation description'),
        required=False,
        missing_value=u'',
    )

    directives.mode(project_dates='display')
    project_dates = schema.Text(
        title=_(u'Project dates'),
    )

    start = schema.Date(
        title=_(u'Starting date'),
        required=True,
        constraint=checkDate
    )

    end = schema.Date(
        title=_(u'Completion date'),
        required=True,
        constraint=checkDate
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

    @invariant
    def validateStartEnd(data):
        if data.start is not None and data.end is not None:
            if data.start > data.end:
                raise StartBeforeEnd(_(u"The starting date must be before the completion date."))


@form.default_value(field=IActivity['currency'])
def projectCurrency(data):
    return data.context.aq_parent.currency


@form.default_value(field=IActivity['project_dates'])
def projectDates(data):
    return "Start date: " + str(data.context.aq_parent.startactual) + " - End date: " + str(data.context.aq_parent.completionactual)


class Edit(form.SchemaEditForm):
    grok.context(IActivity)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
    grok.require('zope2.View')
