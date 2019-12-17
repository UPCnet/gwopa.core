# import datetime
# from DateTime.DateTime import DateTime

from plone import api
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.browser.register import AddUserForm
from plone.app.users.browser.userdatapanel import UserDataPanel
from plone.supermodel import model
from plone.z3cform.fieldsets import extensible
from z3c.form import field
from zope import schema
from zope.component import adapts
from zope.interface import Interface

from gwopa.core import _
from gwopa.core import utils
from gwopa.core.interfaces import IGwopaCoreLayer

from plone import api


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

    position = schema.TextLine(
        title=_(u'Position'),
        description=_(u'Your position in the organization.'),
        required=False
    )

    type_of_organization = schema.Choice(
        title=_(u"Type of organization"),
        required=False,
        source=utils.listTypeOrganizations,
    )

    wop_programs = schema.Choice(
        title=_(u"WOP Program"),
        required=False,
        source=utils.listWOPPrograms,
    )

    wop_platforms = schema.Choice(
        title=_(u'Regional WOP Platform'),
        required=False,
        source=utils.listWOPPlatforms,
    )

    wop_partners = schema.Choice(
        title=_(u"WOP Partners"),
        source=utils.listPartners,
        required=False,
    )

    common_working_areas = schema.List(
        title=_(u"My common Working Areas"),
        required=False,
        value_type=schema.Choice(
            source=utils.area_title,
        ),
    )

    donor = schema.Choice(
        title=_(u"Donor"),
        required=False,
        source=utils.listDonors,
    )

    other = schema.Text(
        title=_(u'Other'),
        required=False,
        default=u"",
    )


class EnhancedUserDataSchemaAdapter(AccountPanelSchemaAdapter):
    schema = IEnhancedUserDataSchema

    def get_wop_programs(self):
        return self._getProperty('wop_programs')

    def set_wop_programs(self, value):
        pc = api.portal.get_tool('portal_catalog')
        user = self.context.id
        #Si inicialmente no habia valor: Se buscan todos los proyectos de ese WOP Program
        #y se anade el permiso para que el usuario pueda editar
        if value and self.context.getProperty('wop_programs') == ():
            items = pc.unrestrictedSearchResults(wop_program=value)
            for item in items:
                project = item.getObject()
                api.user.grant_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                project.reindexObject()
        #Si se quita el valor: Se borran todos los permisos del usuario en los proyectos que tenian el valor antiguo
        if value == None and self.context.getProperty('wop_programs') != ():
            value_old = self.context.getProperty('wop_programs')
            items = pc.unrestrictedSearchResults(wop_program=value_old)
            for item in items:
                project = item.getObject()
                api.user.revoke_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                project.reindexObject()

        #Si habia valor pero se modifica por otro: Se borran todos los permisos del usuario en los proyectos que tenian el valor antiguo
        #y se buscan todos los proyectos de ese nuevo WOP Program seleccionado y se anade el permiso para que el usuario pueda editar
        if value and self.context.getProperty('wop_programs') != ():
            value_old = self.context.getProperty('wop_programs')
            if value != value_old:
                items = pc.unrestrictedSearchResults(wop_program=value_old)
                for item in items:
                    project = item.getObject()
                    api.user.revoke_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                    project.reindexObject()
                items = pc.unrestrictedSearchResults(wop_program=value)
                for item in items:
                    project = item.getObject()
                    api.user.grant_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                    project.reindexObject()

        return self._setProperty('wop_programs', value)

    wop_programs = property(get_wop_programs, set_wop_programs)


    def get_wop_platforms(self):
        return self._getProperty('wop_platforms')

    def set_wop_platforms(self, value):
        pc = api.portal.get_tool('portal_catalog')
        user = self.context.id
        #Si inicialmente no habia valor: Se buscan todos los proyectos de ese WOP Platform
        #y se anade el permiso para que el usuario pueda editar
        if value and self.context.getProperty('wop_platforms') == ():
            items = pc.unrestrictedSearchResults(wop_platform=value)
            for item in items:
                project = item.getObject()
                api.user.grant_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                project.reindexObject()
        #Si se quita el valor: Se borran todos los permisos del usuario en los proyectos que tenian el valor antiguo
        if value == None and self.context.getProperty('wop_platforms') != ():
            value_old = self.context.getProperty('wop_platforms')
            items = pc.unrestrictedSearchResults(wop_platform=value_old)
            for item in items:
                project = item.getObject()
                api.user.revoke_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                project.reindexObject()

        #Si habia valor pero se modifica por otro: Se borran todos los permisos del usuario en los proyectos que tenian el valor antiguo
        #y se buscan todos los proyectos de ese nuevo WOP Platform seleccionado y se anade el permiso para que el usuario pueda editar
        if value and self.context.getProperty('wop_platforms') != ():
            value_old = self.context.getProperty('wop_platforms')
            if value != value_old:
                items = pc.unrestrictedSearchResults(wop_platform=value_old)
                for item in items:
                    project = item.getObject()
                    api.user.revoke_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                    project.reindexObject()
                items = pc.unrestrictedSearchResults(wop_platform=value)
                for item in items:
                    project = item.getObject()
                    api.user.grant_roles(username=user, obj=project, roles=['Editor', 'Reader'])
                    project.reindexObject()

        return self._setProperty('wop_platforms', value)

    wop_platforms = property(get_wop_platforms, set_wop_platforms)


class UserDataPanelExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, UserDataPanel)

    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        roles = api.user.get_roles(username=api.user.get_current().id)
        isAdmin = 'Site Administrator' in roles or 'Manager' in roles
        if not isAdmin:
            fields = fields.omit('type_of_organization')
            fields = fields.omit('wop_programs')
            fields = fields.omit('wop_platforms')
            fields = fields.omit('wop_partners')
            fields = fields.omit('common_working_areas')
            fields = fields.omit('donor')
            fields = fields.omit('other')
        self.add(fields)


class AddUserFormExtender(extensible.FormExtender):
    adapts(Interface, IGwopaCoreLayer, AddUserForm)

    def update(self):
        fields = field.Fields(IEnhancedUserDataSchema)
        self.add(fields)
