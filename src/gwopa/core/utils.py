# -*- coding: utf-8 -*-
from plone import api
from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata
from zope.schema.vocabulary import SimpleTerm
import pycountry
from gwopa.core import _


class vocabulary_values(object):
    """ Generates Multivalue list field """
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
    """ Generates Dropdown with the values """
    vocabulary_list = []
    for row in value:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode('ascii', errors='ignore').decode('ascii'), title=_(row))
        vocabulary_list.append(entry)
    print vocabulary_list
    return SimpleVocabulary(vocabulary_list)


countries = generate_vocabulary([country.name for country in pycountry.countries])
