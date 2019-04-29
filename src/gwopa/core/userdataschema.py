# import datetime
# from DateTime.DateTime import DateTime

from zope.interface import Interface
from zope.component import adapts
from zope import schema

from z3c.form import field

from plone.supermodel import model
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.userdatapanel import UserDataPanel
from plone.app.users.browser.register import AddUserForm
from plone.z3cform.fieldsets import extensible

from gwopa.core.interfaces import IGwopaCoreLayer
from gwopa.core import _
from gwopa.core import utils


class IEnhancedUserDataSchema(model.Schema):
    """ Use all the fields from the default user data schema, and add various
     extra fields.
    """
    language = schema.Choice(
        title=_(u'Language'),
        description=_(u"Define your language"),
        required=True,
        vocabulary=u"plone.app.vocabularies.SupportedContentLanguages",
    )

    phone = schema.TextLine(
        title=_(u'Phone'),
        description=_(u'Your telephone number.'),
        required=False
    )

    country = schema.Choice(
        title=_(u"Country"),
        description=_(u"Select country"),
        vocabulary=utils.countries,
        required=True,
    )

    wop_programs = schema.List(
        title=_(u"WOP Program"),
        required=False,
        value_type=schema.Choice(
            source=utils.listWOPPrograms,
        ),
    )

    wop_platforms = schema.List(
        title=_(u'Regional WOP Platform'),
        required=False,
        value_type=schema.Choice(
            source=utils.listWOPPlatforms
        ),
    )

    wop_partners = schema.Choice(
        title=_(u"WOP Partners"),
        description=_(u""),
        source=utils.listPartners,
        required=False,
    )


class EnhancedUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IEnhancedUserDataSchema


class UserDataPanelExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, UserDataPanel)

    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        self.add(fields)


class AddUserFormExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, AddUserForm)

    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        self.add(fields)
