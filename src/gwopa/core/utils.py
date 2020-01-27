# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.search import quote_chars
from Products.Five.browser import BrowserView

from plone import api
from plone.app.vocabularies.terms import safe_simplevocabulary_from_values
from repoze.catalog.query import Eq
from souper.soup import get_soup
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from gwopa.core import _

import pycountry
import unicodedata


def percentage(part, whole):
    return round(100 * float(part) / float(whole), 0)


def project_currency(self):
    """ Specify the project currency. """
    if hasattr(self, 'context'):
        context = self.context
    else:
        context = self

    currency = getattr(context, 'currency', None)
    if currency:
        item = api.content.find(portal_type="SettingsPage", id='settings')
        if item:
            lang = getUserLang()
            return item[0].getObject().currency_dict[currency][lang].split('-')[-1]
    return '$'


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
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().currency_dict
        terms = []
        for value in values.keys():
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, values[value][lang]))
        return SimpleVocabulary(terms)
    return None


directlyProvides(settings_currency, IContextSourceBinder)


def settings_partner_roles(context):
    """ Currency settings page. """
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().partner_roles_dict
        terms = []
        for value in values.keys():
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, values[value][lang]))
        return SimpleVocabulary(terms)
    return None


directlyProvides(settings_partner_roles, IContextSourceBinder)


def settings_organization_roles(context):
    """ Currency settings page. """
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().organization_roles_dict
        terms = []
        for value in values.keys():
            if value != '':
                flattened = unicodedata.normalize('NFKD', value.decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(value, flattened, values[value][lang]))
        return SimpleVocabulary(terms)
    return None


directlyProvides(settings_organization_roles, IContextSourceBinder)


def getTranslatedCurrencyFromID(unit):
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        currency_dict = item[0].getObject().currency_dict
        return currency_dict[unit][lang]
    return None


def settings_measuring_unit(context):
    """ Measuring Settings. """
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().measuring_unit_dict
        terms = []
        for value in values.keys():
            if value != '':
                flattened = unicodedata.normalize('NFKD', values[value]['en'].decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(values[value]['en'], flattened, values[value][lang]))
        return SimpleVocabulary(terms)
    return None


directlyProvides(settings_measuring_unit, IContextSourceBinder)


def getTranslatedMesuringUnitFromID(unit):
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        measuring_unit_dict = item[0].getObject().measuring_unit_dict
        return measuring_unit_dict[unit][lang]
    return None


def settings_measuring_frequency(context):
    """ Monitoring and reporting frequency settings. """
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item:
        values = item[0].getObject().measuring_frequency_dict
        terms = []
        for value in values.keys():
            if value != '':
                flattened = unicodedata.normalize('NFKD', values[value]['en'].decode('utf-8')).encode('ascii', errors='ignore')
                terms.append(SimpleVocabulary.createTerm(values[value]['en'], flattened, values[value][lang].split(',')[0]))
        return SimpleVocabulary(terms)
    return None


directlyProvides(settings_measuring_frequency, IContextSourceBinder)


def getTranslatedMesuringFrequencyFromID(unit):
    if unit:
        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        if item:
            measuring_frequency_dict = item[0].getObject().measuring_frequency_dict
            if unit in measuring_frequency_dict:
                return measuring_frequency_dict[unit][lang]
    return ''


def getTranslatedDegreeChangesFromID(unit):
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item and unit:
        degree_changes_dict = item[0].getObject().degree_changes_dict
        return degree_changes_dict[unit][lang]
    return None


def getTranslatedContributedProjectFromID(unit):
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item and unit:
        contributed_project_dict = item[0].getObject().contributed_project_dict
        return contributed_project_dict[unit][lang]
    return None


def getTranslatedConsensusFromID(unit):
    lang = getUserLang()
    item = api.content.find(portal_type="SettingsPage", id='settings')
    if item and unit:
        consensus_dict = item[0].getObject().consensus_dict
        return consensus_dict[unit][lang]
    return None


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
    attr_lang = getTitleAttrLang()

    literals = api.content.find(portal_type="ItemArea", context=api.portal.get()['config']['areas'], depth=1)
    for item in literals:
        flattened = unicodedata.normalize('NFKD', item.Title.decode('utf-8')).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item.Title, flattened, getattr(item, attr_lang)))
    return SimpleVocabulary(terms)


directlyProvides(area_title, IContextSourceBinder)


def listTypeOrganizations(context):
    types = []
    types.append(SimpleVocabulary.createTerm(u'Regional WOP Platform', 'Regional WOP Platform', _(u'Regional WOP Platform')))
    types.append(SimpleVocabulary.createTerm(u'WOP Program', 'WOP Program', _(u'WOP Program')))
    types.append(SimpleVocabulary.createTerm(u'Water Operator', 'Water Operator', _(u'Water Operator')))
    types.append(SimpleVocabulary.createTerm(u'Donor', 'Donor', _(u'Donor')))
    types.append(SimpleVocabulary.createTerm(u'Non-participating users', 'Non-participating users', _(u'Non-participating users')))
    types.append(SimpleVocabulary.createTerm(u'Others', 'Others', _(u'Others')))
    return SimpleVocabulary(types)


directlyProvides(listTypeOrganizations, IContextSourceBinder)


def getTitleAttrLang():
    lang = getUserLang()
    return 'Title' if lang == 'en' else 'title_' + lang


def getUserLang():
    lang = api.user.get_current().getProperty('language')

    if not lang or lang == '':
        lang = api.portal.get_default_language()

    return lang


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


def getUsersRegionalWOPPlatform(platform):
    members = api.user.get_users()
    results = []

    if platform:
        for user in members:
            if platform == user.getProperty('wop_platforms'):
                results += [user.id]
    return results


def getUsersWOPProgram(program):
    members = api.user.get_users()
    results = []

    if program:
        for user in members:
            if program == user.getProperty('wop_programs'):
                results += [user.id]
    return results


def getUsersWaterOperator(wateroperator):
    members = api.user.get_users()
    results = []

    if wateroperator:
        for user in members:
            if user.getProperty('wop_partners') in wateroperator:
                results += [user.id]
    return results


def getUsersDonor(donor):
    members = api.user.get_users()
    results = []

    if donor:
        for user in members:
            if user.getProperty('donor') in donor:
                results += [user.id]
    return results


def getDictTranslatedObstaclesFromList(obstacles):
    results = []
    catalog = api.portal.get_tool('portal_catalog')
    attr_lang = getTitleAttrLang()

    if isinstance(obstacles, str) and obstacles != '':
        obstacles = obstacles.split(',')

    for item in obstacles:
        obstacle = catalog.unrestrictedSearchResults(
            portal_type='Mainobstacles',
            Title=item)
        if obstacle:
            results.append({'id': obstacle[0].Title,
                            'text': getattr(obstacle[0], attr_lang)})

    return sorted(results, key=lambda k: k['text'])


def getDictTranslatedContributingFromList(contributings):
    results = []
    catalog = api.portal.get_tool('portal_catalog')
    attr_lang = getTitleAttrLang()

    if isinstance(contributings, str) and contributings != '':
        contributings = contributings.split(',')

    for item in contributings:
        contributing = catalog.unrestrictedSearchResults(
            portal_type='Maincontributing',
            Title=item)
        if contributing:
            results.append({'id': contributing[0].Title,
                            'text': getattr(contributing[0], attr_lang)})

    return sorted(results, key=lambda k: k['text'])


def getTranslatedOutcomesFromTitle(title):
    attr_lang = getTitleAttrLang()
    outcome = api.content.find(
        portal_type=['Outcomedefaults'],
        Title=quote_chars(title.encode('utf-8')))

    return getattr(outcome[0], attr_lang) if outcome else title


class gwopaUtils(BrowserView):
    """ Convenience methods placeholder gwopa.utils view. """

    def canViewFiles(self):
        currentuser = api.user.get_current().id
        pm = getToolByName(self.context, 'portal_membership')
        roles_in_context = pm.getAuthenticatedMember().getRolesInContext(self.context)
        roles = ['Manager', 'Site Administrator', 'Editor']
        for role in roles:
            if role in roles_in_context:
                return True
        if self.context.portal_type != 'Plone Site':
            if self.context.project_manager:
                if currentuser in self.context.project_manager:
                    return True
            if self.context.members:
                if currentuser in self.context.members:
                    return True
        return False

    def canViewPlanningMonitoring(self):
        currentuser = api.user.get_current().id
        pm = getToolByName(self.context, 'portal_membership')
        roles_in_context = pm.getAuthenticatedMember().getRolesInContext(self.context)
        roles = ['Manager', 'Site Administrator', 'Editor']
        for role in roles:
            if role in roles_in_context:
                return True
        if self.context.portal_type != 'Plone Site':
            if self.context.project_manager:
                if currentuser in self.context.project_manager:
                    return True
            if self.context.members:
                if currentuser in self.context.members:
                    return True
        return False

    def canEditPlanningMonitoring(self):
        pm = getToolByName(self.context, 'portal_membership')
        roles_in_context = pm.getAuthenticatedMember().getRolesInContext(self.context)
        roles = ['Manager', 'Site Administrator', 'Editor']
        for role in roles:
            if role in roles_in_context:
                return True
        return False

    def canViewDashboardProject(self):
        currentuser = api.user.get_current().id
        pm = getToolByName(self.context, 'portal_membership')
        roles_in_context = pm.getAuthenticatedMember().getRolesInContext(self.context)
        roles = ['Manager', 'Site Administrator', 'Editor']
        for role in roles:
            if role in roles_in_context:
                return True
        if self.context.portal_type != 'Plone Site':
            if self.context.project_manager:
                if currentuser in self.context.project_manager:
                    return True
            if self.context.members:
                if currentuser in self.context.members:
                    return True
            waterOperators = getUsersWaterOperator(self.context.partners)
            if waterOperators:
                if currentuser in waterOperators:
                    return True
            donors = getUsersDonor(self.context.donors)
            if donors:
                if currentuser in donors:
                    return True

        return False
