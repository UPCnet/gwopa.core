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
    properties = [_(u'username'), _(u'fullname'), _(u'email'), _(u'description'), _(u'location'), _(u'ubicacio'), _(u'telefon'), _(u'twitter_username'), _(u'home_page')]

    profile_properties = ['email', 'description', 'location', 'ubicacio', 'telefon', 'twitter_username', 'home_page']

    directory_properties = ['email', 'telefon', 'location', 'ubicacio']

    directory_icons = {'email': 'fa fa-envelope',
                       'telefon': 'fa fa-mobile',
                       'location': 'fa fa-building-o',
                       'ubicacio': 'fa fa-user'}

    def __call__(self, context):
        catalog = Catalog()
        idindexer = NodeAttributeIndexer('id')
        catalog['id'] = CatalogFieldIndex(idindexer)
        searchable_blob = NodeAttributeIndexer('searchable_text')
        catalog['searchable_text'] = CatalogTextIndex(searchable_blob)
        notlegit = NodeAttributeIndexer('notlegit')
        catalog['notlegit'] = CatalogFieldIndex(notlegit)

        userindexer = NodeAttributeIndexer('username')
        catalog['username'] = CatalogTextIndex(userindexer)
        fullname = NodeAttributeIndexer('fullname')
        catalog['fullname'] = CatalogTextIndex(fullname)
        email = NodeAttributeIndexer('email')
        catalog['email'] = CatalogTextIndex(email)
        location = NodeAttributeIndexer('location')
        catalog['location'] = CatalogTextIndex(location)
        ubicacio = NodeAttributeIndexer('ubicacio')
        catalog['ubicacio'] = CatalogTextIndex(ubicacio)
        telefon = NodeAttributeIndexer('telefon')
        catalog['telefon'] = CatalogTextIndex(telefon)
        twitter_username = NodeAttributeIndexer('twitter_username')
        catalog['twitter_username'] = CatalogTextIndex(twitter_username)
        return catalog


grok.global_utility(UserPropertiesSoupCatalogFactory, name='user_properties')
