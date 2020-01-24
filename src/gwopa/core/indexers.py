from five import grok
from zope.interface import implementer
from repoze.catalog.catalog import Catalog
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from souper.interfaces import ICatalogFactory
from souper.soup import NodeAttributeIndexer

from gwopa.core import _


@implementer(ICatalogFactory)
class UserPropertiesSoupCatalogFactory(object):
    """ The local user catalog (LUC) properties index factory. Almost all the
        properties have a field type "FullTextIndex" to allow wildcard queries
        on them. However, the FullTextIndex has a limitation its supported type
        of queries, so for certain operations is needed a FieldIndex for the
        username.
    """
    properties = [
        _(u'username'),
        _(u'fullname'),
        _(u'email'),
        _(u'description'),
        _(u'wop_platforms'),
        _(u'wop_programs'),
        _(u'wop_partners'),
        _(u'type_of_organization'),
        _(u'common_working_areas'),
        _(u'donor'),
        _(u'other'),
        _(u'country'),
        _(u'position'),
        _(u'phone'),
        _(u'home_page')]

    profile_properties = [
        'email',
        'description',
        'wop_platforms',
        'wop_programs',
        'wop_partners',
        'type_of_organization'
        'common_working_areas',
        'donor',
        'other',
        'country',
        'position',
        'phone',
        'home_page']

    directory_properties = ['email', 'phone', 'wop_platforms', 'wop_programs', 'wop_partners']

    directory_icons = {'email': 'fa fa-envelope',
                       'phone': 'fa fa-mobile',
                       'wop_platforms': 'fa fa-building-o',
                       'wop_programs': 'fa fa-building-o',
                       'wop_partners': 'fa fa-building-o',
                       }

    def __call__(self, context):
        catalog = Catalog()
        idindexer = NodeAttributeIndexer('id')
        catalog['id'] = CatalogFieldIndex(idindexer)

        userindexer = NodeAttributeIndexer('username')
        catalog['username'] = CatalogTextIndex(userindexer)

        fullname = NodeAttributeIndexer('fullname')
        catalog['fullname'] = CatalogTextIndex(fullname)

        email = NodeAttributeIndexer('email')
        catalog['email'] = CatalogTextIndex(email)

        wop_platforms = NodeAttributeIndexer('wop_platforms')
        catalog['wop_platforms'] = CatalogTextIndex(wop_platforms)

        wop_programs = NodeAttributeIndexer('wop_programs')
        catalog['wop_programs'] = CatalogTextIndex(wop_programs)

        wop_partners = NodeAttributeIndexer('wop_partners')
        catalog['wop_partners'] = CatalogTextIndex(wop_partners)

        country = NodeAttributeIndexer('country')
        catalog['country'] = CatalogTextIndex(country)

        position = NodeAttributeIndexer('position')
        catalog['position'] = CatalogTextIndex(position)

        type_of_organization = NodeAttributeIndexer('type_of_organization')
        catalog['type_of_organization'] = CatalogTextIndex(type_of_organization)

        common_working_areas = NodeAttributeIndexer('common_working_areas')
        catalog['common_working_areas'] = CatalogTextIndex(common_working_areas)

        donors = NodeAttributeIndexer('donors')
        catalog['donors'] = CatalogTextIndex(donors)

        other_info = NodeAttributeIndexer('other_info')
        catalog['other_info'] = CatalogTextIndex(other_info)

        return catalog


grok.global_utility(UserPropertiesSoupCatalogFactory, name='user_properties')


@implementer(ICatalogFactory)
class NotifyReportsSoupCatalogFactory(object):
    """ The local user catalog (LUC) properties index factory. Almost all the
        properties have a field type "FullTextIndex" to allow wildcard queries
        on them. However, the FullTextIndex has a limitation its supported type
        of queries, so for certain operations is needed a FieldIndex for the
        username.

        :index id: FieldIndex - The group id for exact queries
        :index searchable_id: FullTextIndex - The group id used for wildcard
            queries
    """
    def __call__(self, context):
        catalog = Catalog()
        projectindexer = NodeAttributeIndexer('id')
        catalog['id'] = CatalogFieldIndex(projectindexer)

        project_url = NodeAttributeIndexer('project_url')
        catalog['project_url'] = CatalogTextIndex(project_url)

        project_title = NodeAttributeIndexer('project_title')
        catalog['project_title'] = CatalogTextIndex(project_title)

        email = NodeAttributeIndexer('email')
        catalog['email'] = CatalogTextIndex(email)

        date_email_report = NodeAttributeIndexer('date_email_report')
        catalog['date_email_report'] = CatalogTextIndex(date_email_report)

        date_generate_report = NodeAttributeIndexer('date_generate_report')
        catalog['date_generate_report'] = CatalogTextIndex(date_generate_report)

        return catalog


grok.global_utility(NotifyReportsSoupCatalogFactory, name='notify_reports')
