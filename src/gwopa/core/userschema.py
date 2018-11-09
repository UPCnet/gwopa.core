# -*- coding: utf-8 -*-
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.register import BaseRegistrationForm
from plone.app.users.browser.userdatapanel import UserDataPanel
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from z3c.form import field
from zope import schema
from zope.component import adapts
from zope.interface import Interface

from gwopa.core import _
from gwopa.core.interfaces import IGwopaCoreLayer


class IDemoUserSchema(model.Schema):

    twitter_username = schema.TextLine(
        title=_(u'Twitter username'),
        description=_(u'Fill in your Twitter username.'),
        required=False,
    )

    ubicacio = schema.TextLine(
        title=_(u'Location'),
        description=_(u'help_location'),
        required=False,
    )

    telefon = schema.TextLine(
        title=_(u'Phone'),
        description=_(u'help_phone'),
        required=False,
    )


class DemoUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IDemoUserSchema


class DemoUserDataPanelExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, UserDataPanel)


class DemoRegistrationPanelExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, BaseRegistrationForm)

    def update(self):
        fields = field.Fields(IDemoUserSchema)
        self.add(fields)
