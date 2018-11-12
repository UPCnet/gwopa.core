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
from gwopa.core import utils

from gwopa.core import _
from gwopa.core.interfaces import IGwopaCoreLayer


class IDemoUserSchema(model.Schema):

    language = schema.Choice(
        title=_(u'Language'),
        description=_(u"Define your language"),
        required=True,
        vocabulary=u"plone.app.vocabularies.SupportedContentLanguages",
    )

    twitter_username = schema.TextLine(
        title=_(u'Twitter username'),
        description=_(u'Your Twitter username. Could include the @. Example: @unhabitat'),
        required=False,
    )

    telefon = schema.TextLine(
        title=_(u'Phone'),
        description=_(u'Your telephone number.'),
        required=False,
    )
    country = schema.Choice(
        title=_(u"Country"),
        description=_(u"Select country"),
        vocabulary=utils.countries,
        required=True,
    )

    ubicacio = schema.TextLine(
        title=_(u'Location'),
        description=_(u'Your location - either city and country - or in a company setting, where your office is located.'),
        required=False,
    )

    region = schema.List(
        title=_(u'Region'),
        required=False,
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.region_list'),
        ),
    )

    wop_program = schema.List(
        title=_(u"WOP Program"),
        description=_(u"Program/programs associated to this project"),
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.wop_list'),
        ),
        required=False,
    )

    wop_platform = schema.List(
        title=_(u'WOP Platform'),
        required=False,
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.wop_platform'),
        ),
    )

    partners = schema.List(
        title=_(u"Partners"),
        description=_(u"Partner/partners associated to this project"),
        required=False,
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.partners_list'),
        ),
    )

    arees_exp = schema.List(
        title=_(u'Experimental Areas'),
        required=False,
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.experimental_areas'),
        ),
    )
    # OK Nombre completo del usuario (obligatorio)
    # OK Nombre de usuario (obligatorio)
    # OK Email de contacto del usuario (obligatorio)
    # OK Teléfono de contacto (opcional)
    # OK Ubicación. Lista cerrada de países (opcional)
    # OK Idioma del usuario (a elegir entre inglés, francés o español). Por defecto inglés.
    # Región. Lista cerrada de regiones (opcional). Definida la región, se incluyen los países asociados
    # WOP Platform. Lista cerrada de plataformas regionales (opcional)
    # WOP Program. Lista cerrada de programas WOP (opcional) multi
    # Water Operator (partner). Lista cerrada (Obligatorio) (partner list)  uniq
    # Áreas de experiencia (lista cerrada) (opcional) controlpanel

    # Default fields and added ones:
    # Fullname
    # email
    # User name
    # password
    # confirm password
    # twitter
    # location
    # Phone


class DemoUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IDemoUserSchema


class DemoUserDataPanelExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, UserDataPanel)


class DemoRegistrationPanelExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, BaseRegistrationForm)

    def update(self):
        fields = field.Fields(IDemoUserSchema)
        self.add(fields)
