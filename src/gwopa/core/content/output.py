# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.directives import form
from z3c.form.interfaces import IAddForm, IEditForm

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


def endDefaultValue():
    return datetime.datetime.today() + datetime.timedelta(10)


class IOutput(model.Schema):
    """  Output
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    initial_situation = schema.Text(
        title=_(u'Initial situation description'),
        required=False,
        missing_value=u'',
    )

    end = schema.Datetime(
        title=_(u'Completion time'),
        required=True,
        defaultFactory=endDefaultValue
    )

    target = schema.Text(
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

    form.mode(gwopa_year='hidden')
    form.mode(IEditForm, gwopa_year='display')
    form.mode(IAddForm, gwopa_year='hidden')
    gwopa_year = schema.TextLine(
        title=_(u'Internal code (YEAR)'),
        description=_(u'Internal code used only by administrators.'),
        required=False)


@form.default_value(field=IOutput['gwopa_year'])
def codeDefaultValue(data):
    return data.request.form['year']


class View(grok.View):
    grok.context(IOutput)
    grok.template('output_view')
