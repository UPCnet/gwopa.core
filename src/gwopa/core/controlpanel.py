# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.registry.browser import controlpanel
from zope import schema
from plone.supermodel import model


class IGWOPASettings(model.Schema):

    wop_list = schema.List(
        title=_(u'WOP Program list'),
        description=_(u'Available WOP Programs in the portal. One per line.'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    wop_platform = schema.List(
        title=_(u'WOP Platform'),
        description=_(u'Available WOP Platform in the portal. One per line.'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    partners_list = schema.List(
        title=_(u'Partners list'),
        description=_(u'Available Partners shown in the portal. One per line.'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    region_list = schema.List(
        title=_(u'Regions list'),
        description=_(u'Available Regions used in the portal. One per line.'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    currency = schema.List(
        title=_(u'Currency Exchange'),
        description=_(u'Used in the projects item. One per line.'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    experimental_areas = schema.List(
        title=_(u'Experimental Areas list'),
        description=_(u'Available Experimental Areas used in the portal. One per line.'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    measuring_unit = schema.List(
        title=_(u'Measuring unit'),
        description=_(u'Used in indicators'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    measuring_frequency = schema.List(
        title=_(u'Measuring frequency'),
        description=_(u'Used in indicators'),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )

    capacity_changes = schema.List(
        title=_(u'Capacity Changes'),
        description=_(u''),
        required=False,
        default=[u''],
        value_type=schema.TextLine(),
        missing_value=(),
    )


class GwopaControlPanelForm(controlpanel.RegistryEditForm):

    schema = IGWOPASettings
    id = "GwopaControlPanelForm"
    description = _(u'All this parameters are needed for the correct use of GWOPA PMP system.')
    label = _(u"GWOPA Settings")

    def updateFields(self):
        super(GwopaControlPanelForm, self).updateFields()

    def updateWidgets(self):
        super(GwopaControlPanelForm, self).updateWidgets()


class GwopaEditingControlPanel(controlpanel.ControlPanelFormWrapper):
    form = GwopaControlPanelForm
