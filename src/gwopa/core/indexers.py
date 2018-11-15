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
        _(u'region'),
        _(u'country'),
        _(u'phone'),
        _(u'twitter_username'),
        _(u'home_page')]

    profile_properties = [
        'email',
        'description',
        'region',
        'country',
        'phone',
        'twitter_username',
        'home_page']

    directory_properties = ['email', 'phone', 'region']

    directory_icons = {'email': 'fa fa-envelope',
                       'phone': 'fa fa-mobile',
                       'region': 'fa fa-building-o'}

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

        region = NodeAttributeIndexer('region')
        catalog['region'] = CatalogTextIndex(region)

        country = NodeAttributeIndexer('country')
        catalog['country'] = CatalogTextIndex(country)

        twitter_username = NodeAttributeIndexer('twitter_username')
        catalog['twitter_username'] = CatalogTextIndex(twitter_username)
        return catalog


grok.global_utility(UserPropertiesSoupCatalogFactory, name='user_properties')
