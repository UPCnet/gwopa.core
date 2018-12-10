# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from z3c.form.interfaces import HIDDEN_MODE  # INPUT_MODE, DISPLAY_MODE
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
        description=_(u'Used in the projects item. One per line.'),
        required=True,
    )

    measuring_unit = schema.Text(
        title=_(u'Measuring unit'),
        description=_(u'Used in indicators'),
        required=True,
    )

    measuring_frequency = schema.Text(
        title=_(u'Measuring frequency'),
        description=_(u'Used in indicators'),
        required=True,
    )

    capacity_changes = schema.Text(
        title=_(u'Capacity Changes'),
        description=_(u''),
        required=True,
    )


class View(grok.View):
    grok.context(ISettingspage)
    grok.template('settings_view')


class Edit(form.SchemaEditForm):
    grok.context(ISettingspage)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["description"].mode = HIDDEN_MODE
