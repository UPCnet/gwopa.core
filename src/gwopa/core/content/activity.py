# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
# from zope.interface import Invalid
# from zope.interface import invariant
from gwopa.core import utils
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from plone.directives import form
from z3c.form.interfaces import IAddForm, IEditForm

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


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

    start = schema.Date(
        title=_(u'Starting date'),
        required=True,
        defaultFactory=todayValue
    )

    end = schema.Date(
        title=_(u'Completion date'),
        required=True,
        defaultFactory=todayValue
    )

    budget = schema.Text(
        title=_(u'Assigned budget'),
        required=False,
        missing_value=u'',
    )

    directives.mode(currency='display')
    currency = schema.Text(
        title=_(u''),
    )

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )


@form.default_value(field=IActivity['currency'])
def projectCurrency(data):
    return data.context.aq_parent.currency


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
    grok.require('zope2.View')
