# -*- coding: utf-8 -*-
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata
from zope.schema.vocabulary import SimpleTerm
import pycountry
from gwopa.core import _
from souper.soup import get_soup
from repoze.catalog.query import Eq
from zope.interface import directlyProvides


def generate_vocabulary(value):
    """ Generates Dropdown with the countries """
    vocabulary_list = []
    for row in value:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode('ascii', errors='ignore').decode('ascii'), title=_(row))
        vocabulary_list.append(entry)
    return SimpleVocabulary(vocabulary_list)


countries = generate_vocabulary([country.name for country in pycountry.countries])


def listWOPPlatforms(context):
    """ WOP Platforms are like regions """
    terms = []
    literals = api.content.find(portal_type="Platform")
    for item in literals:
        flattened = unicodedata.normalize('NFKD', item.Title.decode('utf-8')).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item.Title, flattened, item.Title))
    return SimpleVocabulary(terms)


directlyProvides(listWOPPlatforms, IContextSourceBinder)


def listPartners(context):
    """ WOP Partners list """
    terms = []
    literals = api.content.find(portal_type="Partner")
    for item in literals:
        flattened = unicodedata.normalize('NFKD', item.Title.decode('utf-8')).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item.Title, flattened, item.Title))
    return SimpleVocabulary(terms)


directlyProvides(listPartners, IContextSourceBinder)


def listWOPPrograms(context):
    """ WOP Programs """
    terms = []
    literals = api.content.find(portal_type="Program")
    for item in literals:
        flattened = unicodedata.normalize('NFKD', item.Title.decode('utf-8')).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item.Title, flattened, item.Title))
    return SimpleVocabulary(terms)


directlyProvides(listWOPPrograms, IContextSourceBinder)


def settings_currency(context):
    """ Currency settings page """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().currency
        terms = []
        for value in values.split('\n'):
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, value))
        return SimpleVocabulary(terms)
    else:
        return None


directlyProvides(settings_currency, IContextSourceBinder)


def settings_measuring_unit(context):
    """ Measuring Settings """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().measuring_unit
        terms = []
        for value in values.split('\n'):
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, value))
        return SimpleVocabulary(terms)
    else:
        return None


directlyProvides(settings_measuring_unit, IContextSourceBinder)


def settings_measuring_frequency(context):
    """ Measuring frequency settings """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().measuring_frequency
        terms = []
        for value in values.split('\n'):
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, value))
        return SimpleVocabulary(terms)
    else:
        return None


directlyProvides(settings_measuring_frequency, IContextSourceBinder)


def settings_capacity_changes(context):
    """ Capacity changes settings """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().capacity_changes
        terms = []
        for value in values.split('\n'):
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, value))
        return SimpleVocabulary(terms)
    else:
        return None


directlyProvides(settings_capacity_changes, IContextSourceBinder)


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
