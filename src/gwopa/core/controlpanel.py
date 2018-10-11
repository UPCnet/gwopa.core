# -*- coding: utf-8 -*-
from Products.CMFPlone import PloneMessageFactory as _
from plone.app.registry.browser import controlpanel
from zope import schema
from plone.supermodel import model


class IGWOPASettings(model.Schema):

    wop_list = schema.Text(
        title=_(u'WOP Program list'),
        description=_(u'Available WOP Programs in the portal. One per line.'),
        default=u'',
        required=False
    )

    partners_list = schema.Text(
        title=_(u'Partners list'),
        description=_(u'Available Partners shown in the portal. One per line.'),
        default=u'',
        required=False
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
