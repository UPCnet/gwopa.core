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

    twitter_username = schema.TextLine(
        title=_(u'Twitter username'),
        description=_(u'Your Twitter username. Could include the @. Example: @unhabitat'),
        required=False,
    )

    birthdate = schema.Date(
        title=_(u'label_birthdate', default=u'Birthdate'),
        description=_(u'help_birthdate',
                      default=u'Your date of birth, in the format dd-mm-yyyy'),
        required=False,
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

    region = schema.Choice(
        title=_(u'Region'),
        required=False,
        source=utils.listRegions
    )
    # source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.region_list'),

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


class EnhancedUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IEnhancedUserDataSchema

    # def get_birthdate(self):
    #     bd = self._getProperty('birthdate')
    #     return None if bd == '' else bd.asdatetime().date()

    # def set_birthdate(self, value):
    #     return self._setProperty('birthdate', DateTime(datetime.datetime(value.year, value.month, value.day, 0, 0)))

    # birthdate = property(get_birthdate, set_birthdate)


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
