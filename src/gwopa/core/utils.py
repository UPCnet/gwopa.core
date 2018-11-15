# -*- coding: utf-8 -*-
from plone import api
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata
from zope.schema.vocabulary import SimpleTerm
import pycountry
from gwopa.core import _
from souper.soup import get_soup
from repoze.catalog.query import Eq


class vocabulary_values(object):
    """ Generates Vocabulary list field """
    implements(IContextSourceBinder)

    def __init__(self, key):
        self.key = key

    def __call__(self, context):
        values = api.portal.get_registry_record(self.key)
        terms = []
        for item in values:
            if len(item.lstrip()) != 0:
                if isinstance(item, str):
                    flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
                else:
                    flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(item, flattened, item))
        return SimpleVocabulary(terms)


def generate_vocabulary(value):
    """ Generates Dropdown with the countries """
    vocabulary_list = []
    for row in value:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode('ascii', errors='ignore').decode('ascii'), title=_(row))
        vocabulary_list.append(entry)
    return SimpleVocabulary(vocabulary_list)


countries = generate_vocabulary([country.name for country in pycountry.countries])


def get_safe_member_by_id(username):
    """Gets user info from the repoze.catalog based user properties catalog.
       This is a safe implementation for getMemberById portal_membership to
       avoid useless searches to the LDAP server. It gets only exact matches (as
       the original does) and returns a dict. It DOES NOT return a Member
       object.
    """
    portal = api.portal.get()
    soup = get_soup('user_properties', portal)
    username = username.lower()
    try:
        records = [r for r in soup.query(Eq('id', username))]
    except:
        records = None
    if records:
        properties = {}
        for attr in records[0].attrs:
            if records[0].attrs.get(attr, False):
                properties[attr] = records[0].attrs[attr]

        # Make sure that the key 'fullname' is returned anyway for it's used in
        # the wild without guards
        if 'fullname' not in properties:
            properties['fullname'] = ''

        return properties
    else:
        # No such member: removed?  We return something useful anyway.
        return {
            'username': username,
            'description': '',
            'language': '',
            'home_page': '',
            'name_or_id': username,
            'location': '',
            'fullname': ''}
