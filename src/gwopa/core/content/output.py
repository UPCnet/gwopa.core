# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
# from plone.directives import form
from z3c.form.interfaces import IAddForm, IEditForm
from plone.autoform import directives
from plone.app.z3cform.widget import SelectWidget
from gwopa.core import utils
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

    target = schema.TextLine(
        title=_(u"Measurable Target"),
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

    # form.mode(gwopa_year='hidden')
    # form.mode(IEditForm, gwopa_year='hidden')
    # form.mode(IAddForm, gwopa_year='hidden')
    # gwopa_year = schema.Int(
    #     title=_(u'Internal code (YEAR)'),
    #     description=_(u'Internal code used only by administrators.'),
    #     required=False)


# @form.default_value(field=IOutput['gwopa_year'])
# def codeDefaultValue(data):
#     if 'year' in data.request.form:
#         return int(data.request.form['year'])
#     else:
#         return datetime.datetime.now().year


class View(grok.View):
    grok.context(IOutput)
    grok.template('output_view')
    grok.require('zope2.View')
