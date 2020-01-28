# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.directives import form
# from z3c.form.interfaces import IAddForm, IEditForm
from plone.autoform import directives
from plone.app.z3cform.widget import SelectWidget
from gwopa.core import utils
from z3c.form.interfaces import DISPLAY_MODE

grok.templatedir("templates")


def todayValue():
    return datetime.datetime.today()


class IOutput(model.Schema):
    """  Output
    """
    title = schema.TextLine(
        title=_(u"Numeration - Title"),
        description=_(u"(e.g. 1.1 - Trained Staff)"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    directives.mode(project_dates='display')
    project_dates = schema.Text(
        title=_(u''),
    )

    measuring_unit = schema.Choice(
        title=_(u"Measuring unit"),
        source=utils.settings_measuring_unit,
        required=True,
    )

    end = schema.Datetime(
        title=_(u'Completion date'),
        required=True,
        defaultFactory=todayValue
    )

    means = schema.Text(
        title=_(u"Means of verification"),
        required=False,
    )

    # risks = schema.Text(
    #     title=_(u"Risks / Assumptions"),
    #     required=False,
    # )


    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )

@form.default_value(field=IOutput['project_dates'])
def projectDates(data):
    return "The dates must be between the limits of this Project. Start: " + str(data.context.aq_parent.startactual) + " End: " + str(data.context.aq_parent.completionactual)


class Edit(form.SchemaEditForm):
    grok.context(IOutput)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        # self.widgets["title"].mode = DISPLAY_MODE


class View(grok.View):
    grok.context(IOutput)
    grok.template('output_view')
    grok.require('zope2.View')
