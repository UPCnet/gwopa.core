# -*- coding: utf-8 -*-
from plone import api
from zope.schema.interfaces import IContextSourceBinder
from plone.app.vocabularies.terms import safe_simplevocabulary_from_values
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata
from zope.schema.vocabulary import SimpleTerm
import pycountry
from gwopa.core import _
from souper.soup import get_soup
from repoze.catalog.query import Eq
from Products.CMFCore.utils import getToolByName
from zope.interface import directlyProvides


def percentage(part, whole):
    return round(100 * float(part) / float(whole), 0)


def project_currency(self):
    """ Specify the project currency. """
    currency = getattr(self.context, 'currency', None)
    if currency:
        letter = currency.split('-')[-1].lstrip(' ').rstrip(' ')
    else:
        letter = '$'
    return letter


def getPortrait(self, user):
    """ Get Personal Portrait from user. """
    membership_tool = getToolByName(
        self.context, 'portal_membership'
    )
    return membership_tool.getPersonalPortrait(user)


def generate_vocabulary(value):
    """ Generates Dropdown with the countries. """
    vocabulary_list = []
    for row in value:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode(
            'ascii', errors='ignore').decode('ascii'), title=_(row))
        vocabulary_list.append(entry)
    return SimpleVocabulary(vocabulary_list)


countries = generate_vocabulary([country.name for country in pycountry.countries])


def listWOPPlatforms(context):
    """ WOP Platforms are like regions. """
    terms = []
    literals = api.content.find(portal_type="Platform")
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(listWOPPlatforms, IContextSourceBinder)


def listPartners(context):
    """ WOP Partners list. """
    terms = []
    literals = api.content.find(portal_type="Partner")
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(listPartners, IContextSourceBinder)


def listDonors(context):
    """ Donors list. """
    terms = []
    literals = api.content.find(portal_type="Donor")
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(listDonors, IContextSourceBinder)


def listWOPPrograms(context):
    """ WOP Programs. """
    terms = []
    literals = api.content.find(portal_type="Program")
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(listWOPPrograms, IContextSourceBinder)


def settings_currency(context):
    """ Currency settings page. """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().currency
        terms = []
        for value in values.split('\r\n'):
            if value != '':
                terms.append(value)
        return safe_simplevocabulary_from_values(terms)
    else:
        return None


directlyProvides(settings_currency, IContextSourceBinder)


def settings_measuring_unit(context):
    """ Measuring Settings. """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().measuring_unit
        terms = []
        for value in values.split('\n'):
            if value != '':
                terms.append(value)
        return safe_simplevocabulary_from_values(terms)
    else:
        return None


directlyProvides(settings_measuring_unit, IContextSourceBinder)


def settings_measuring_frequency(context):
    """ Monitoring and reporting frequency settings. """
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().measuring_frequency
        terms = []
        for value in values.split('\n'):
            if value != '':
                terms.append(value.split(',')[0])
        return safe_simplevocabulary_from_values(terms)
    else:
        return None


directlyProvides(settings_measuring_frequency, IContextSourceBinder)


def settings_capacity_changes(context):
    """ Capacity changes settings. """
    items = api.content.find(portal_type="OutcomeCCItem")
    terms = []
    for item in items:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(settings_capacity_changes, IContextSourceBinder)


def contextAreas(context):
    """ Get context areas. """
    terms = []
    literals = api.content.find(portal_type="ImprovementArea", context=context)
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(contextAreas, IContextSourceBinder)


def outputs(context):
    """ Outputs for the Activity. """
    terms = []
    literals = api.content.find(portal_type="Output", context=context, depth=1)
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(outputs, IContextSourceBinder)


def area_title(context):
    """ Titles of Improvement Areas. """
    terms = []
    literals = api.content.find(portal_type="ItemArea", context=api.portal.get()[
                                'config']['areas'], depth=1)
    for item in literals:
        terms.append(item.Title)
    return safe_simplevocabulary_from_values(terms)


directlyProvides(area_title, IContextSourceBinder)


def get_safe_member_by_id(username):
    """
    Gets user info from the repoze.catalog based user properties catalog.

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
