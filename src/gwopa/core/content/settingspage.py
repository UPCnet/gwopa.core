# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from z3c.form.interfaces import HIDDEN_MODE
# from z3c.form.interfaces import INPUT_MODE
from z3c.form.interfaces import DISPLAY_MODE
from plone.directives import form

grok.templatedir("templates")


class ISettingspage(model.Schema):
    """  Settings Page """

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"The system will use the settings id. Change for testing purposes only."),
        required=True,
        default=_(u'settings'),
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        default=_(u'This values are necessary for create elements on the Platform'),
    )

    currency = schema.Text(
        title=_(u"Currency Exchange"),
        description=_(u'One per line, string and symbol merged with a dash. Ex: USD-US Dollar-$'),
        required=True,
    )

    measuring_unit = schema.Text(
        title=_(u'Measuring unit'),
        description=_(u'One unit per line. Ex: liters'),
        required=True,
    )

    measuring_frequency = schema.Text(
        title=_(u'Monitoring and reporting frequency'),
        description=_(u'A string and the number of notifications per year, separated by comma. One per line. Ex: Annually,1'),
        required=True,
    )

    degree_changes = schema.Text(
        title=_(u'Degree changes'),
        description=_(u'Perceived degree of change'),
        required=True,
    )

    contributed_project = schema.Text(
        title=_(u'Contributed project'),
        description=_(u'Project contribution to the perceived change'),
        required=True,
    )

    consensus = schema.Text(
        title=_(u'Consensus'),
        description=_(u'Perceived change decided by'),
        required=True,
    )


# class View(grok.View):
#     grok.context(ISettingspage)
#     grok.template('settings_view')
#     grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(ISettingspage)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["description"].mode = DISPLAY_MODE
