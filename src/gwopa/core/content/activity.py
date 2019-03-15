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

    # inputs = schema.Text(
    #     title=_(u'Related inputs'),
    #     required=False,
    #     missing_value=u'',
    # )

    budget = schema.Text(
        title=_(u'Assigned budget'),
        required=False,
        missing_value=u'',
    )

    # milestones = schema.Text(
    #     title=_(u'Milestones'),
    #     required=False,
    #     missing_value=u'',
    # )

    # directives.widget('outputs', SelectWidget)
    # outputs = schema.List(
    #     title=_(u"Related outputs"),
    #     value_type=schema.Choice(
    #         source=utils.outputs),
    #     required=False,
    # )

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )

    # area = schema.Choice(
    #     title=_(u"Related Improvement Areas"),
    #     required=False,
    #     source=utils.contextAreas
    # )

    form.mode(gwopa_year='hidden')
    form.mode(IEditForm, gwopa_year='hidden')
    form.mode(IAddForm, gwopa_year='hidden')
    gwopa_year = schema.Int(
        title=_(u'Internal code (YEAR)'),
        description=_(u'Internal code used only by administrators.'),
        required=False)

    form.mode(gwopa_code_hash='hidden')
    form.mode(IEditForm, gwopa_code_hash='hidden')
    form.mode(IAddForm, gwopa_code_hash='hidden')
    gwopa_code_hash = schema.TextLine(
        title=_(u'GWOPA CODE HASH'),
        required=False)


@form.default_value(field=IActivity['gwopa_year'])
def codeDefaultValue(data):
    if 'year' in data.request.form:
        return int(data.request.form['year'])
    else:
        return datetime.datetime.now().year


@form.default_value(field=IActivity['gwopa_code_hash'])
def hashValue(data):
    """ ACT-M-2019"""
    if 'year' in data.request.form:
        return 'ACT-M-' + data.request.form['year']
    else:
        return 'ACT-M-' + str(datetime.datetime.now().year)


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
    grok.require('zope2.View')
