# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.statusmessages.interfaces import IStatusMessage

from cgi import parse_qs
from five import grok
from plone import api
from plone.app.dexterity.behaviors import constrains
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from random import random
from requests.exceptions import ConnectionError
from zope.interface import alsoProvides

from gwopa.core import _
from gwopa.core.content.project import default_plus_one_year
from gwopa.core.content.project import default_today
from gwopa.core.content.settingspage import updateDictsSetting
from gwopa.core.interfaces import IGwopaCoreLayer

import logging
import math
import requests

requests.packages.urllib3.disable_warnings()


grok.templatedir("templates")


def _setup_constrains(container, allowed_types):
    behavior = ISelectableConstrainTypes(container)
    behavior.setConstrainTypesMode(constrains.ENABLED)
    behavior.setImmediatelyAddableTypes(allowed_types)
    return True


class setup(grok.View):
    grok.name('setup_home')
    grok.template('setup_home')
    grok.context(IPloneSiteRoot)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.ManagePortal')

    def update(self):
        qs = self.request.get('QUERY_STRING', None)
        if qs is not None:
            query = parse_qs(qs)
            if 'create' in query:
                logger = logging.getLogger('# Executed setup_home on Site ->')
                logger.info('%s' % self.context.id)
                self.apply_default_language_settings()
                self.createConfigFolders()
                self.createDefaultValues()
                # self.request.response.redirect(self.context.absolute_url())
            if 'createdemocontent' in query:
                logger = logging.getLogger('# Creating DEMO CONTENT on Site ->')
                logger.info('%s' % self.context.id)
                self.createUsers()
                self.createDemoContent()
                message = _(u"Demo content has been created.")
                IStatusMessage(self.request).addStatusMessage(message, type="warning")
                logger = logging.getLogger('# DEMO CONTENT HAS BEEN CREATED!')
                logger.info('%s' % self.context.id)
                # self.request.response.redirect(self.context.absolute_url())

    def apply_default_language_settings(self):
        pl = api.portal.get_tool('portal_languages')
        pl.removeSupportedLanguages(pl.getSupportedLanguages())
        pl.addSupportedLanguage('en')
        pl.addSupportedLanguage('es')
        pl.addSupportedLanguage('fr')
        pl.setDefaultLanguage('en')

    def createConfigFolders(self):
        """ Method that creates all the default content """
        portal = api.portal.get()

        # Get rid of the original page
        if getattr(portal, 'front-page', False):
            api.content.delete(obj=portal['front-page'], check_linkintegrity=False)

        # Delete 'Members', 'news' and 'events' folders
        if getattr(portal, 'Members', False):
            api.content.delete(obj=portal['Members'], check_linkintegrity=False)
        if getattr(portal, 'news', False):
            api.content.delete(obj=portal['news'], check_linkintegrity=False)
        if getattr(portal, 'events', False):
            api.content.delete(obj=portal['events'], check_linkintegrity=False)

        # Set the default pages to the homepage view
        portal.setLayout('homepage')
        messages = IStatusMessage(self.request)
        try:
            config_folder = api.content.create(
                type='Folder',
                id='config',
                title='Config folder',
                Description='This folder contains configuration folders used in the Site and managed by the administrators',
                container=portal,
                safe_id=False)
            config_folder.setLayout('tabular_view')
            allowed_types = ['Folder', ]
            _setup_constrains(config_folder, allowed_types)

            programs = api.content.create(
                type='Folder',
                id='programs',
                title='WOP Programs',
                description='WOP Programs',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Program', ]
            _setup_constrains(programs, allowed_types)

            platforms = api.content.create(
                type='Folder',
                id='platforms',
                title='WOP Platforms',
                description='WOP Platforms',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Platform', ]
            _setup_constrains(platforms, allowed_types)

            partners = api.content.create(
                type='Folder',
                id='partners',
                title='WOP Partners',
                description='WOP Partners',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Partner', ]
            _setup_constrains(partners, allowed_types)

            donors = api.content.create(
                type='Folder',
                id='donors',
                title='Donors',
                description='Donors',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Donor', ]
            _setup_constrains(donors, allowed_types)

            areas = api.content.create(
                type='Folder',
                id='areas',
                title='Default Working Areas values',
                description='Working Areas used in the projects',
                container=config_folder,
                safe_id=False)
            allowed_types = ['ItemArea', ]
            _setup_constrains(areas, allowed_types)

            outcomes = api.content.create(
                type='Folder',
                id='capacitychanges',
                title='Default Capacity Changes values',
                description='Values used in OutcomeCC and OutcomeCCS',
                container=config_folder,
                safe_id=False)
            allowed_types = ['OutcomeCCItem', ]
            _setup_constrains(outcomes, allowed_types)

            # outputs = api.content.create(
            #     type='Folder',
            #     id='outputs',
            #     title='Default Output values',
            #     description='Default title outputs used in projects',
            #     container=config_folder,
            #     safe_id=False)
            # allowed_types = ['Outputdefaults', ]
            # _setup_constrains(outputs, allowed_types)

            outcomes = api.content.create(
                type='Folder',
                id='outcomes',
                title='Default Outcome values',
                description='Default title outcomes used in projects',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Outcomedefaults', ]
            _setup_constrains(outcomes, allowed_types)

            projects = api.content.create(
                type='Folder',
                id='projects',
                title='Projects',
                description='Projects of the Platform',
                container=portal,
                safe_id=False)
            allowed_types = ['Project', ]
            _setup_constrains(projects, allowed_types)
            # projects.setLayout('facetednavigation_view')  TODO: Por ahora hacerlo a mano...
            # IFacetedNavigable(projects)
            # IDisableSmartFacets(projects)
            # IHidePloneLeftColumn(projects)
            # IHidePloneRightColumn(projects)

            mainobstacles = api.content.create(
                type='Folder',
                id='mainobstacles',
                title='Default Main Obstacles values',
                description='Default title Main Obstacles used in project monitoring',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Mainobstacles', ]
            _setup_constrains(mainobstacles, allowed_types)

            maincontributing = api.content.create(
                type='Folder',
                id='maincontributing',
                title='Default Main Contributing values',
                description='Default title Main Contributing factors used in project monitoring',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Maincontributing', ]
            _setup_constrains(maincontributing, allowed_types)

            partnershippractice = api.content.create(
                type='Folder',
                id='partnershippractice',
                title='Default Partnership Practice values',
                description='Partnership Practice used in the projects',
                container=config_folder,
                safe_id=False)
            allowed_types = ['IPartnershipPractice', ]
            _setup_constrains(partnershippractice, allowed_types)

            message = _(u"The default config has been applied.")
            messages.addStatusMessage(message, type="info")
        except Exception, e:
            # Show friendly error message
            messages.addStatusMessage(unicode(e), 'error')

    def createDefaultValues(self):
        """ Assign default values to panel control options """

        portal = api.portal.get()
        settingspage = api.content.create(
            type='SettingsPage',
            id='settings',
            title='GWOPA Settings Page',
            description='GWOPA default values used in Site',
            container=portal.config,
            safe_id=False)
        settingspage.currency = 'USD-US Dollar-$\r\nEUR-Euro-€\r\nGBP-British Pound-£\r\nAUD-Australian Dollar-$\r\nCAD-Canadian Dollar-$'
        settingspage.measuring_unit = 'liters\nm3\npeople\nconnections\nhouseholds\nkilometers\nstaff by population\nstaff by connection\ncost recovery ratio\nworkplace accidents\nworker satisfaction\ndays\nhours\npercentage\nother'
        settingspage.measuring_frequency = 'Annually,1\nBiannually,2\nQuarterly,4'
        settingspage.degree_changes = '-2 Very negative\n-1 Negative\n0 No change\n1 Positive\n2 Very positive'
        settingspage.contributed_project = '0 No contribution\n1 Fair contribution\n2 Very high contribution'
        settingspage.consensus = 'One Partner\nWop Partners'
        settingspage.partner_roles = 'Mentor\nMentee'
        settingspage.organization_roles = 'Broker (matchmaker, facilitator)\nTechnical Support\nPolitical Support'

        settingspage.currency_es = 'USD-Dólar estadounidense-$\r\nEUR-Euro-€\r\nGBP-Libra británica-£\r\nAUD-Dólar australiano-$\r\nCAD-Dolar canadiense-$'
        settingspage.measuring_unit_es = 'litros\nm3\npersonas\nconexiones\nhogares\nkilómetros\npersonal por población\npersonal por conexión\ntasa de recuperación de costos\naccidentes laborales\nsatisfacción laboral\nhoras\ndias\nporcentaje\notro'
        settingspage.measuring_frequency_es = 'Anualmente,1\nBianualmente,2\nTrimestralmente,4'
        settingspage.degree_changes_es = '-2 Muy negativo\n-1 Negativo\n0 Sin cambios\n1 Positivo\n2 Muy positivo'
        settingspage.contributed_project_es = '0 Sin contribución\n1 Contribución justa\n2 Contribución muy alta'
        settingspage.consensus_es = 'Un Partner\nWop Partners'
        settingspage.partner_roles_es = 'Mentor\nAprendiz'
        settingspage.organization_roles_es = 'Corredor (facilitador)\nSoporte técnico\nSoporte político'

        # TODO: Falta traducir los valores al Frances
        settingspage.currency_fr = 'USD-US Dollar-$\r\nEUR-Euro-€\r\nGBP-British Pound-£\r\nAUD-Australian Dollar-$\r\nCAD-Canadian Dollar-$'
        settingspage.measuring_unit_fr = 'litres\nm3\npersonnes\nconnections\nménages\nkilomètres\npersonnel par population\npersonnel par connexion\nratio de recouvrement des coûts\naccidents du travail\nsatisfaction des travailleurs\nheures\njours\npercentage\nautre'
        settingspage.measuring_frequency_fr = 'Annuellement,1\nTous les deux ans,2\nTrimestriel,4'
        settingspage.degree_changes_fr = '-2 Very negative\n-1 Negative\n0 No change\n1 Positive\n2 Very positive'
        settingspage.contributed_project_fr = '0 No contribution\n1 Fair contribution\n2 Very high contribution'
        settingspage.consensus_fr = 'One Partner\nWop Partners'
        settingspage.partner_roles_fr = 'Mentor\nMentee'
        settingspage.organization_roles_fr = 'Broker (matchmaker, facilitator)\nTechnical Support\nPolitical Support'

        settingspage.reindexObject()
        updateDictsSetting(settingspage)

        portal = api.portal.get()

        # Create base Outcome CC selectable Values
        tool_ts = getToolByName(self, 'translation_service')
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Vision, mission and strategy'),
            title_es=tool_ts.translate(u'Vision, mission and strategy', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Vision, mission and strategy', domain='gwopa', target_language='fr'),
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Leadership'),
            title_es=tool_ts.translate(u'Leadership', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Leadership', domain='gwopa', target_language='fr'),
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Organizational culture'),
            title_es=tool_ts.translate(u'Organizational culture', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Organizational culture', domain='gwopa', target_language='fr'),
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'External relations / networking'),
            title_es=tool_ts.translate(u'External relations / networking', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'External relations / networking', domain='gwopa', target_language='fr'),
            icon='fab fa-industry',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Resource acquisition'),
            title_es=tool_ts.translate(u'Resource acquisition', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Resource acquisition', domain='gwopa', target_language='fr'),
            icon='fas fa-sitemap',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Structure'),
            title_es=tool_ts.translate(u'Structure', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Structure', domain='gwopa', target_language='fr'),
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Management practices'),
            title_es=tool_ts.translate(u'Management practices', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Management practices', domain='gwopa', target_language='fr'),
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Systems'),
            title_es=tool_ts.translate(u'Systems', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Systems', domain='gwopa', target_language='fr'),
            icon='fas fa-map',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Information'),
            title_es=tool_ts.translate(u'Information', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Information', domain='gwopa', target_language='fr'),
            icon='fas fa-tree',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Equipment and infrastructure'),
            title_es=tool_ts.translate(u'Equipment and infrastructure', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Equipment and infrastructure', domain='gwopa', target_language='fr'),
            icon='fas fa-university',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Working routines'),
            title_es=tool_ts.translate(u'Working routines', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Working routines', domain='gwopa', target_language='fr'),
            icon='fas fa-cogs',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Individual skills / abilities'),
            title_es=tool_ts.translate(u'Individual skills / abilities', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Individual skills / abilities', domain='gwopa', target_language='fr'),
            icon='fab fa-industry',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Staff motivation'),
            title_es=tool_ts.translate(u'Staff motivation', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Staff motivation', domain='gwopa', target_language='fr'),
            icon='fas fa-users',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title=_(u'Applied knowledge / skills'),
            title_es=tool_ts.translate(u'Applied knowledge / skills', domain='gwopa', target_language='es'),
            title_fr=tool_ts.translate(u'Applied knowledge / skills', domain='gwopa', target_language='fr'),
            icon='fas fa-search',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)

        # Create item areas
        working_areas = [
            _(u'Asset Management'),
            _(u'Billing & Collection Efficiency'),
            _(u'Business Planning'),
            _(u'Commercial & Physical Losses - NRW'),
            _(u'Customer Service'),
            _(u'Financial Management'),
            _(u'Wastewater Collection & Treatment'),
            _(u'Production Processes & Service Quality & Water Safety (Drinking Water)'),
            _(u'Operation & Maintenance'),
            _(u'Energy Efficiency'),
            _(u'Human Resource Management/ Organizational Development'),
            _(u'Corporate Governance & Institutions'),
            _(u'Catchment Management/ IWRM'),
            _(u'Climate Change Resilience'),
            _(u'Services in Low-Income Areas'),
            _(u'Extension of Sanitation & Hygiene Services'),
            _(u'Extension of Water Supply Services'),
            _(u'Social Inclusion/ Gender'),
            _(u'Information & Technology'),
            _(u'Policy and Legal Support'),
            _(u'Water Demand Management')
        ]

        tool_ts = getToolByName(self, 'translation_service')
        for i in working_areas:
            title_es = tool_ts.translate(i, domain='gwopa', target_language='es')
            title_fr = tool_ts.translate(i, domain='gwopa', target_language='fr')
            obj = api.content.create(
                type='ItemArea',
                id=i,
                title=i,
                title_es=title_es if title_es != '' else i,
                title_fr=title_fr if title_fr != '' else i,
                container=portal.config.areas,
                safe_id=True)

            obj.image = self.getRandomImage(200, 200)
        self.createDefaultOutputs()
        self.createDefaultOutcomes()
        self.createDefaultMainObstacles()
        self.createDefaultMainContributing()
        self.createDefaultPartnershippractice()
        return "Default values content created"

    def createUsers(self):
        for i in xrange(1, 6):
            try:
                properties = dict(
                    fullname='Test User' + str(i),
                )
                api.user.create(
                    username='user' + str(i),
                    email='user' + str(i) + '@test.com',
                    password='user' + str(i),
                    properties=properties,
                )
            except:
                pass

    def createDemoContent(self):
        """ Create Demo Content """

        portal = api.portal.get()

        # Create demo Platforms
        wop_platforms = [
            "Cari-WOP",
            "PWWA",
            "WaterLinks",
            "WOP-Africa",
            "WOP-LAC",
            "P-WOP (Pakistan)",
            "PERPAMSI (Indonesia)"]
        for i in wop_platforms:
            obj = api.content.create(
                type='Platform',
                title=str(i),
                container=portal.config.platforms,
                safe_id=False)
            obj.country = ['Spain']

        # Create demo Programs
        wop_programs = [
            "WaterWorX",
            "OFID"]
        for i in wop_programs:
            obj = api.content.create(
                type='Program',
                title=str(i),
                container=portal.config.programs,
                safe_id=False)
            obj.contact = 'userprogram' + str(i) + '@test.com'
            obj.country = ['Spain']

        # Create demo partners
        portal = api.portal.get()
        for i in xrange(1, 6):
            obj = api.content.create(
                type='Partner',
                id='partner' + str(i),
                title='WOP Partner ' + str(i),
                description='WOP Partner ' + str(i),
                container=portal.config.partners,
                safe_id=False)
            obj.contact = 'userpartner' + str(i) + '@test.com'
            obj.country = ['Spain']
            obj.latitude, obj.longitude = self.randomgeo()

        # Create demo donors
        portal = api.portal.get()
        for i in xrange(1, 6):
            obj = api.content.create(
                type='Donor',
                id='donor' + str(i),
                title='Donor ' + str(i),
                description='Donor ' + str(i),
                container=portal.config.donors,
                safe_id=False)
            obj.contact = 'userdonor' + str(i) + '@test.com'
            obj.country = ['Spain']

        self.createProjects(5)
        return "Demo content created"

    def getRandomImage(self, w, h):
        """ Valid topics keys:
                abstract, city, people, transport, animals, food, nature
                business, nightlife, sports, cats, fashion, technics

                    https://dummyimage.com/600x400/eaeaea/aeaeae
                    http://lorempixel.com/

        """
        try:
            # data = requests.get('http://dummyimage.com/{0}x{1}/aeaeae/ffffff'.format(w, h), verify=False, timeout=10).content
            data = requests.get('http://placeimg.com/{0}/{1}/tech'.format(w, h), verify=False, timeout=10).content
        except:
            data = requests.get(api.portal.get().aq_parent.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg', verify=False, timeout=10).content
        image = NamedBlobImage(data=data,
                               filename=u'image.jpg',
                               contentType='image/jpeg')
        return image

    def getLoremIpsum(self, number, length, type_code):
        """ Returns Lorem Ipsum text """
        try:
            text = requests.get('http://loripsum.net/api/{0}/{1}/{2}'.format(number, type_code, length), verify=False, timeout=10).content
        except ConnectionError:
            return "</ Empty field because no network response from http://loripsum.net />"
        return text

    def createProjects(self, number):
        portal = api.portal.get()
        for i in range(number):
            project = api.content.create(
                type='Project',
                id='project' + str(int(i + 1)),
                title='Demo Project ' + str(int(i + 1)),
                container=portal['projects'],
                startactual=default_today(self),
                completionactual=default_plus_one_year(self),
                safe_id=True)
            project.image = self.getRandomImage(200, 200)
            project.contribution = RichTextValue(
                self.getLoremIpsum(2, 'long', 'html'),
                'text/html', 'text/html')
            new_value = []
            project.partners = new_value
            project.assumptions = project.contribution
            project.objectives = project.contribution
            project.country = 'Spain'
            project.latitude, project.longitude = self.randomgeo()

    def randomgeo(self):
        # Random lat and long to geopositioning Projects
        t = 2 * math.pi * random()
        u = random() + random()
        radius = int(random() * 100)
        if u > 1:
            r = 2 - u
        else:
            r = u
        return radius * r * math.cos(t), radius * r * math.sin(t)

    def createDefaultOutputs(self):
        titles = [
            _(u'Leadership development program prepared'),
            _(u'Business plan developed/improved'),
            _(u'Management information system introduced/improved'),
            _(u'Internal audit performed on transparency and integrity'),
            _(u'Improvement plan drawn up based on internal audit'),
            _(u'Yearly benchmark report prepared'),
            _(u'Organisation improvement plan developed'),
            _(u'Capacity development program prepared'),
            _(u'NRW reduction plan developed'),
            _(u'Number of people trained in NRW reduction approach'),
            _(u'Maintenance and management program developed'),
            _(u'Number of people trained in maintenance and management'),
            _(u'Development of an improvement plan for sanitation, sewage and waste water treatment'),
            _(u'Pro-poor coordinators appointed and trained'),
            _(u'Pro-poor vision, strategy and objectives developed'),
            _(u'Proposals developed for providing people with direct acces to improved water and/ or sanitation facilities'),
            _(u'Coordination of the implementation of the proposals'),
            _(u'Climate resistant water supply program 2050 developed'),
            _(u'Energy saving program developed'),
            _(u'Gender analysis and approach developed')
        ]

        # tool_ts = getToolByName(self, 'translation_service')
        # portal = api.portal.get()
        # for item in titles:
        #     title_es = tool_ts.translate(item, domain='gwopa', target_language='es')
        #     title_fr = tool_ts.translate(item, domain='gwopa', target_language='fr')
        #     api.content.create(
        #         type='Outputdefaults',
        #         title=item,
        #         title_es=title_es if title_es != '' else item,
        #         title_fr=title_fr if title_fr != '' else item,
        #         container=portal.config.outputs,
        #         safe_id=True)

    def createDefaultOutcomes(self):
        titles = [
            _(u'Total number of connections'),
            _(u'Total number of people served'),
            _(u'Coverage'),
            _(u'(Estimated) coverage LIA population'),
            _(u'% Female employees'),
            _(u'% Female employees in management positions'),
            _(u'Number of FT employees per 1000 active connections'),
            _(u'NRW in m3 per actve connection per year'),
            _(u'NRW as percentage of system input'),
            _(u'Collection efficiency'),
            _(u'Customer satisfaction'),
            _(u'Working ratio'),
            _(u'Operating ratio'),
            _(u'Debt service coverage ratio (DSCR)'),
            _(u'Energy consumption per m3 system input'),
            _(u'Expenditures on chemicals per m3 system input'),
            _(u'Chlorine consumption per m3 system input'),
            _(u'Aluminium sulphate consumption per m3 system input'),
            _(u'Percentage of required checks carried out for faecal coliform'),
            _(u'Percentage of checks that do not comply with norm on faecal coliform'),
            _(u'Percentage of required checks carried out for residual chlorine'),
            _(u'Percentage of checks that do not comply with norm on residual Chlorine'),
            _(u'Number of people with access to improved sanitation facilities'),
            _(u'Percentage of people with access to improved sanitation facilities'),
            _(u'Number of people with access to unimproved sanitation facilities'),
            _(u'Percentage of people with access to unimproved sanitation facilities'),
            _(u'Total number of sewerage connections'),
            _(u'Percentage of waste water treated'),
        ]

        tool_ts = getToolByName(self, 'translation_service')
        portal = api.portal.get()
        for item in titles:
            title_es = tool_ts.translate(item, domain='gwopa', target_language='es')
            title_fr = tool_ts.translate(item, domain='gwopa', target_language='fr')
            api.content.create(
                type='Outcomedefaults',
                title=item,
                title_es=title_es if title_es != '' else item,
                title_fr=title_fr if title_fr != '' else item,
                container=portal.config.outcomes,
                safe_id=True)

    def createDefaultMainObstacles(self):
        titles = [
            _(u'Internal organizational'),
            _(u'External environment'),
            _(u'WOP project - related'),
        ]

        tool_ts = getToolByName(self, 'translation_service')
        portal = api.portal.get()
        for item in titles:
            title_es = tool_ts.translate(item, domain='gwopa', target_language='es')
            title_fr = tool_ts.translate(item, domain='gwopa', target_language='fr')
            api.content.create(
                type='Mainobstacles',
                title=item,
                title_es=title_es if title_es != '' else item,
                title_fr=title_fr if title_fr != '' else item,
                container=portal.config.mainobstacles,
                safe_id=True)

    def createDefaultMainContributing(self):
        titles = [
            _(u'Internal organizational'),
            _(u'External environment'),
            _(u'WOP project - related'),
        ]

        tool_ts = getToolByName(self, 'translation_service')
        portal = api.portal.get()
        for item in titles:
            title_es = tool_ts.translate(item, domain='gwopa', target_language='es')
            title_fr = tool_ts.translate(item, domain='gwopa', target_language='fr')
            api.content.create(
                type='Maincontributing',
                title=item,
                title_es=title_es if title_es != '' else item,
                title_fr=title_fr if title_fr != '' else item,
                container=portal.config.maincontributing,
                safe_id=True)


    def createDefaultPartnershippractice(self):
        titles = [
            _(u'Set Up'),
            _(u'Roles and responsibilities'),
            _(u'Meeting processes'),
            _(u'Work processes'),
            _(u'Communication and transparency'),
            _(u'Trust and teamwork'),
            _(u'Partnership adaptation and sustainability'),
            _(u'Resourses'),
        ]

        descriptions = [
            _(u'Description Set Up'),
            _(u'Description Roles and responsibilities'),
            _(u'Description Meeting processes'),
            _(u'Description Work processes'),
            _(u'Description Communication and transparency'),
            _(u'Description Trust and teamwork'),
            _(u'Description Partnership adaptation and sustainability'),
            _(u'Description Resourses'),
        ]
        tool_ts = getToolByName(self, 'translation_service')
        portal = api.portal.get()
        for item in titles:
            title_es = tool_ts.translate(item, domain='gwopa', target_language='es')
            title_fr = tool_ts.translate(item, domain='gwopa', target_language='fr')
            for description in descriptions:
                description_es = tool_ts.translate(description, domain='gwopa', target_language='es')
                description_fr = tool_ts.translate(description, domain='gwopa', target_language='fr')

            api.content.create(
                type='PartnershipPractice',
                title=item,
                title_es=title_es if title_es != '' else item,
                title_fr=title_fr if title_fr != '' else item,
                description_es=description_es if description_es != '' else item,
                description_fr=description_fr if description_fr != '' else item,
                container=portal.config.partnershippractice,
                safe_id=True)

class setupEs(grok.View):
    grok.name('setup_home_es')
    grok.template('setup_home_es')
    grok.context(IPloneSiteRoot)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.ManagePortal')

    def update(self):
        qs = self.request.get('QUERY_STRING', None)
        if qs is not None:
            query = parse_qs(qs)
            if 'create' in query:
                logger = logging.getLogger('# Executed setup_home on Site ->')
                logger.info('%s' % self.context.id)
                self.apply_default_language_settings()
                self.createConfigFolders()
                # self.request.response.redirect(self.context.absolute_url())
            if 'createdemocontent' in query:
                logger = logging.getLogger('# Creating DEMO CONTENT on Site ->')
                logger.info('%s' % self.context.id)
                self.createDemoContent()
                message = _(u"Demo content has been created.")
                IStatusMessage(self.request).addStatusMessage(message, type="warning")
                logger = logging.getLogger('# DEMO CONTENT HAS BEEN CREATED!')
                logger.info('%s' % self.context.id)
                # self.request.response.redirect(self.context.absolute_url())

    def apply_default_language_settings(self):
        pl = api.portal.get_tool('portal_languages')
        pl.removeSupportedLanguages(pl.getSupportedLanguages())
        pl.addSupportedLanguage('en')
        pl.addSupportedLanguage('es')
        pl.addSupportedLanguage('fr')
        pl.setDefaultLanguage('es')

    def createConfigFolders(self):
        """ Method that creates all the default content """
        portal = api.portal.get()

        # Get rid of the original page
        if getattr(portal, 'front-page', False):
            api.content.delete(obj=portal['front-page'], check_linkintegrity=False)

        # Delete 'Members', 'news' and 'events' folders
        if getattr(portal, 'Members', False):
            api.content.delete(obj=portal['Members'], check_linkintegrity=False)
        if getattr(portal, 'news', False):
            api.content.delete(obj=portal['news'], check_linkintegrity=False)
        if getattr(portal, 'events', False):
            api.content.delete(obj=portal['events'], check_linkintegrity=False)

        # Set the default pages to the homepage view
        portal.setLayout('homepage')
        messages = IStatusMessage(self.request)
        try:
            config_folder = api.content.create(
                type='Folder',
                id='config',
                title='Config folder',
                Description='This folder contains configuration folders used in the Site and managed by the administrators',
                container=portal,
                safe_id=False)
            config_folder.setLayout('tabular_view')
            allowed_types = ['Folder', ]
            _setup_constrains(config_folder, allowed_types)

            programs = api.content.create(
                type='Folder',
                id='programs',
                title='WOP Programas',
                description='WOP Programas',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Program', ]
            _setup_constrains(programs, allowed_types)

            platforms = api.content.create(
                type='Folder',
                id='platforms',
                title='WOP Platformas',
                description='WOP Platformas',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Platform', ]
            _setup_constrains(platforms, allowed_types)

            partners = api.content.create(
                type='Folder',
                id='partners',
                title='WOP Patrocinadores',
                description='WOP Patrocinadores',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Partner', ]
            _setup_constrains(partners, allowed_types)

            donors = api.content.create(
                type='Folder',
                id='donors',
                title='Donantes',
                description='Donantes',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Donor', ]
            _setup_constrains(donors, allowed_types)

            areas = api.content.create(
                type='Folder',
                id='areas',
                title='Valores por defecto de las áreas de trabajo',
                description='Áreas de trabajo utilizadas en los proyectos.',
                container=config_folder,
                safe_id=False)
            allowed_types = ['ItemArea', ]
            _setup_constrains(areas, allowed_types)

            outcomes = api.content.create(
                type='Folder',
                id='capacitychanges',
                title='Valores por defecto de los cambios de capacidad',
                description='Valores usados en OutcomeCC y OutcomeCCS',
                container=config_folder,
                safe_id=False)
            allowed_types = ['OutcomeCCItem', ]
            _setup_constrains(outcomes, allowed_types)

            outputs = api.content.create(
                type='Folder',
                id='outputs',
                title='Valores por defecto Output',
                description='Título por defecto de los outputs usados en proyectos',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Outputdefaults', ]
            _setup_constrains(outputs, allowed_types)

            outcomes = api.content.create(
                type='Folder',
                id='outcomes',
                title='Valores por defecto Outcome',
                description='Título por defecto de los outcomes usados en proyectos',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Outcomedefaults', ]
            _setup_constrains(outcomes, allowed_types)

            projects = api.content.create(
                type='Folder',
                id='projects',
                title='Proyectos',
                description='Proyectos de la Plataforma',
                container=portal,
                safe_id=False)
            allowed_types = ['Project', ]
            _setup_constrains(projects, allowed_types)
            # projects.setLayout('facetednavigation_view')  TODO: Por ahora hacerlo a mano...
            # IFacetedNavigable(projects)
            # IDisableSmartFacets(projects)
            # IHidePloneLeftColumn(projects)
            # IHidePloneRightColumn(projects)

            mainobstacles = api.content.create(
                type='Folder',
                id='mainobstacles',
                title='Valores por defecto de los principales obstáculos',
                description='Título por defecto de los principales obstáculos utilizados en la supervisión del proyecto',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Mainobstacles', ]
            _setup_constrains(mainobstacles, allowed_types)

            maincontributing = api.content.create(
                type='Folder',
                id='maincontributing',
                title='Valores por defecto de los contribuyentes principales',
                description='Título por defecto de los principales factores contribuyentes utilizados en el monitoreo del proyecto',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Maincontributing', ]
            _setup_constrains(maincontributing, allowed_types)

            message = _(u"Se ha aplicado la configuración por defecto.")
            messages.addStatusMessage(message, type="info")
        except Exception, e:
            # Show friendly error message
            messages.addStatusMessage(unicode(e), 'error')

    def createDemoContent(self):
        """ Assign default values to panel control options """
        for i in xrange(1, 41):
            try:
                properties = dict(
                    fullname='Test User' + str(i),
                    location='Barcelona',
                )
                api.user.create(
                    username='user' + str(i),
                    email='user' + str(i) + '@test.com',
                    password='user' + str(i),
                    properties=properties,
                )
            except:
                pass

        portal = api.portal.get()
        settingspage = api.content.create(
            type='SettingsPage',
            id='settings',
            title='Página de configuración GWOPA',
            description='Valores por defecto usados en GWOPA',
            container=portal.config,
            safe_id=False)
        settingspage.currency = 'USD-Dólar Estadounidense-$\r\nEUR-Euro-€\r\nGBP-Libra Esterlina-£\r\nAUD-Dólar Australiano-$\r\nCAD-Dólar Canadiense-$'
        settingspage.measuring_unit = 'litros\nm3\npersonas\notros'
        settingspage.measuring_frequency = 'Anual,1\nBianual,2\nTrimestral,4'
        settingspage.degree_changes = '-2 Muy negativo\n-1 Negativo\n0 Sin cambios\n1 Positivo\n2 Muy positivo'
        settingspage.contributed_project = '0 Sin contribución\n1 Contribución justa\n2 Contribución muy alta'
        settingspage.consensus = 'Un patrocinador\nWop Patrocinador'

        portal = api.portal.get()

        # Create demo Platforms
        wop_platforms = [
            "Cari-WOP",
            "PWWA",
            "WaterLinks",
            "WOP-Africa",
            "WOP-LAC",
            "P-WOP (Pakistan)",
            "PERPAMSI (Indonesia)"]
        for i in wop_platforms:
            obj = api.content.create(
                type='Platform',
                title=str(i),
                container=portal.config.platforms,
                safe_id=False)
            obj.country = ['Spain']

        # Create demo Programs
        wop_programs = [
            "WaterWorX",
            "OFID"]
        for i in wop_programs:
            obj = api.content.create(
                type='Program',
                title=str(i),
                container=portal.config.programs,
                safe_id=False)
            obj.contact = 'userprogram' + str(i) + '@test.com'
            obj.country = ['Spain']

        # Create demo partners
        portal = api.portal.get()
        for i in xrange(1, 6):
            obj = api.content.create(
                type='Partner',
                id='partner' + str(i),
                title='WOP Patrocinador ' + str(i),
                description='WOP Patrocinador ' + str(i),
                container=portal.config.partners,
                safe_id=False)
            obj.contact = 'userpartner' + str(i) + '@test.com'
            obj.country = ['Spain']
            obj.latitude, obj.longitude = self.randomgeo()

        # Create demo donors
        portal = api.portal.get()
        for i in xrange(1, 6):
            obj = api.content.create(
                type='Donor',
                id='donor' + str(i),
                title='Donante ' + str(i),
                description='Donante ' + str(i),
                container=portal.config.donors,
                safe_id=False)
            obj.contact = 'userdonor' + str(i) + '@test.com'
            obj.country = ['Spain']
            obj.latitude, obj.longitude = self.randomgeo()

        # Create base Outcome CC selectable Values
        api.content.create(
            type='OutcomeCCItem',
            title='Misión y estrategia',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Liderazgo',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Cultura Organizativa',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Recursos externos',
            icon='fab fa-industry',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Red / Relaciones externas',
            icon='fas fa-sitemap',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Sistemas',
            icon='fas fa-map',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Estructura',
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Administración',
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Información',
            icon='fas fa-tree',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Infraestructura / Equipamiento',
            icon='fas fa-university',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Rutinas de trabajo',
            icon='fas fa-cogs',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Habilidades y Conocimiento',
            icon='fab fa-industry',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Motivación',
            icon='fas fa-users',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Conocimientos aplicados',
            icon='fas fa-search',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)

        # Create item areas
        working_areas = [
            'Gestión de activos',
            'Facturación y Eficiencia de recolección',
            'Planificación empresarial',
            'Comercial y Pérdidas Físicas - NRW',
            'Servicio al cliente',
            'Gestión financiera',
            'Recogida y Tratamiento de aguas residuales',
            'Procesos de producción, Servicios de Calidad y Seguridad del agua (agua potable)',
            'Operación y Mantenimiento',
            'Eficiencia energética',
            'Gestión de recursos humanos / Desarrollo organizacional',
            'Gobierno Corporativo e Instituciones',
            'Gestión de captación / IWRM',
            'Resiliencia al cambio climático',
            'Servicios en zonas de bajos ingresos',
            'Ampliación de los servicios de saneamiento e higiene',
            'Ampliación de los Servicios de abastecimiento de agua',
            'Inclusión social / género',
            'Información y Tecnología',
            'Política y soporte legal',
            'Gestión de la demanda de agua',
        ]

        for i in working_areas:
            obj = api.content.create(
                type='ItemArea',
                id=str(i),
                title=str(i),
                container=portal.config.areas,
                safe_id=True)
            obj.image = self.getRandomImage(200, 200)
        self.createProjects(5)
        self.createDefaultOutputs()
        self.createDefaultOutcomes()
        self.createDefaultMainObstacles()
        self.createDefaultMainContributing()
        return "Contenido demo creado"

    def getRandomImage(self, w, h):
        """ Valid topics keys:
                abstract, city, people, transport, animals, food, nature
                business, nightlife, sports, cats, fashion, technics

                    https://dummyimage.com/600x400/eaeaea/aeaeae
                    http://lorempixel.com/

        """
        try:
            # data = requests.get('http://dummyimage.com/{0}x{1}/aeaeae/ffffff'.format(w, h), verify=False, timeout=10).content
            data = requests.get('http://placeimg.com/{0}/{1}/tech'.format(w, h), verify=False, timeout=10).content
        except:
            data = requests.get(api.portal.get().aq_parent.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg', verify=False, timeout=10).content
        image = NamedBlobImage(data=data,
                               filename=u'image.jpg',
                               contentType='image/jpeg')
        return image

    def getLoremIpsum(self, number, length, type_code):
        """ Returns Lorem Ipsum text """
        try:
            text = requests.get('http://loripsum.net/api/{0}/{1}/{2}'.format(number, type_code, length), verify=False, timeout=10).content
        except ConnectionError:
            return "</ Empty field because no network response from http://loripsum.net />"
        return text

    def createProjects(self, number):
        portal = api.portal.get()
        for i in range(number):
            project = api.content.create(
                type='Project',
                id='project' + str(int(i + 1)),
                title='Proyecto demo ' + str(int(i + 1)),
                container=portal['projects'],
                startactual=default_today(self),
                completionactual=default_plus_one_year(self),
                safe_id=True)
            project.image = self.getRandomImage(200, 200)
            project.contribution = RichTextValue(
                self.getLoremIpsum(2, 'long', 'html'),
                'text/html', 'text/html')
            new_value = []
            project.partners = new_value
            project.assumptions = project.contribution
            project.objectives = project.contribution
            project.country = 'Spain'
            project.latitude, project.longitude = self.randomgeo()

    def randomgeo(self):
        # Random lat and long to geopositioning Projects
        t = 2 * math.pi * random()
        u = random() + random()
        radius = int(random() * 100)
        if u > 1:
            r = 2 - u
        else:
            r = u
        return radius * r * math.cos(t), radius * r * math.sin(t)

    def createDefaultOutputs(self):
        titles = [
            'Programa de desarrollo de liderazgo preparado',
            'Plan de negocios desarrollado / mejorado',
            'Sistema de información de gestión introducido / mejorado',
            'Auditoría interna realizada sobre transparencia e integridad',
            'Plan de mejora elaborado en base a auditoría interna',
            'Informe anual de referencia elaborado',
            'Plan de mejora organizativa desarrollado',
            'Programa de desarrollo de capacidades preparado',
            'Plan de reducción de NRW desarrollado',
            'Número de personas capacitadas en el enfoque de reducción de NRW',
            'Programa de mantenimiento y gestión desarrollado',
            'Número de personas formadas en mantenimiento y gestión',
            'Desarrollo de un plan de mejora de saneamiento, alcantarillado y tratamiento de aguas residuales',
            'Coordinadores pro-pobres nombrados y entrenados',
            'Visión pro-pobre, estrategia y objetivos desarrollados',
            'Propuestas desarrolladas para brindar a las personas acceso directo a instalaciones mejoradas de agua y / o saneamiento',
            'Coordinación de la implementación de las propuestas',
            'Programa de suministro de agua resistente al clima 2050 desarrollado',
            'Programa de ahorro de energía desarrollado',
            'Análisis de género y enfoque desarrollado'
        ]
        portal = api.portal.get()
        for item in titles:
            api.content.create(
                type='Outputdefaults',
                title=item,
                title_es=item,
                title_fr=item,
                container=portal.config.outputs,
                safe_id=True)

    def createDefaultOutcomes(self):
        titles = [
            'Número total de conexiones',
            'Número total de personas atendidas',
            'Cobertura',
            '(Estimated) coverage LIA population',
            '% Empleadas',
            '% Empleadas en puestos directivos',
            'Número de empleados de FT por 1000 conexiones activas',
            'NRW en m3 por conexión activa por año',
            'NRW como porcentaje de entrada del sistema',
            'Eficiencia de recolección',
            'La satisfacción del cliente',
            'Relación de trabajo',
            'Relación de operación',
            'Relación de cobertura de servicio de la deuda (DSCR)',
            'Consumo de energía por m3 de entrada del sistema',
            'Gastos en productos químicos por m3 de entrada al sistema',
            'Consumo de cloro por m3 del sistema de entrada',
            'Consumo de sulfato de aluminio por m3 de entrada del sistema',
            'Porcentaje de controles requeridos para coliformes fecales',
            'Porcentaje de cheques que no cumplen con la norma sobre coliformes fecales',
            'Porcentaje de controles requeridos para cloro residual',
            'Porcentaje de controles requeridos realizados para Porcentaje de controles que no cumplen con la norma sobre cloro residual',
            'Número de personas con acceso a instalaciones sanitarias mejoradas',
            'Porcentaje de personas con acceso a instalaciones sanitarias mejoradas',
            'Número de personas con acceso a instalaciones sanitarias no mejoradas',
            'Porcentaje de personas con acceso a instalaciones sanitarias no mejoradas',
            'Número total de conexiones de alcantarillado',
            'Porcentaje de aguas residuales tratadas',
        ]
        portal = api.portal.get()
        for item in titles:
            api.content.create(
                type='Outcomedefaults',
                title=item,
                title_es=item,
                title_fr=item,
                container=portal.config.outcomes,
                safe_id=True)

    def createDefaultMainObstacles(self):
        titles = [
            'Organizacion interna',
            'Ambiente externo',
            'Proyecto WOP - relacionado',
        ]
        portal = api.portal.get()
        for item in titles:
            api.content.create(
                type='Mainobstacles',
                title=item,
                title_es=item,
                title_fr=item,
                container=portal.config.outputs,
                safe_id=True)

    def createDefaultMainContributing(self):
        titles = [
            'Organizacion interna',
            'Ambiente externo',
            'Proyecto WOP - relacionado',
        ]
        portal = api.portal.get()
        for item in titles:
            api.content.create(
                type='Maincontributing',
                title=item,
                title_es=item,
                title_fr=item,
                container=portal.config.outputs,
                safe_id=True)


class addReportContentInProjects(grok.View):
    grok.context(IPloneSiteRoot)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.ManagePortal')

    def render(self):
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            alsoProvides(self.request, IDisableCSRFProtection)
        except:
            pass

        catalog = api.portal.get_tool('portal_catalog')
        projects = catalog.unrestrictedSearchResults(portal_type='Project')
        for project in projects:
            project = project.getObject()
            if 'reports' in project:
                behavior = ISelectableConstrainTypes(project['reports'])
                behavior.setConstrainTypesMode(1)
                behavior.setLocallyAllowedTypes(('File', 'Report'))
                behavior.setImmediatelyAddableTypes(('File', 'Report'))


class setupPartnership(grok.View):
    grok.name('setup_partnershippractive')
    grok.context(IPloneSiteRoot)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.ManagePortal')

    def render(self):

        config_folder = api.content.find(type='Folder',id='config')
        config_folder = config_folder[0].getObject()
        partnershippractice = api.content.create(
                type='Folder',
                id='partnershippractice',
                title='Default Partnership Practice values',
                description='Partnership Practice used in the projects',
                container=config_folder,
                safe_id=False)
        allowed_types = ['PartnershipPractice', ]
        _setup_constrains(partnershippractice, allowed_types)

        self.createDefaultPartnershippractice()

    def createDefaultPartnershippractice(self):
        titles = [
            _(u'Set Up'),
            _(u'Roles and responsibilities'),
            _(u'Meeting processes'),
            _(u'Work processes'),
            _(u'Communication and transparency'),
            _(u'Trust and teamwork'),
            _(u'Partnership adaptation and sustainability'),
            _(u'Resourses'),
        ]

        descriptions = [
            _(u'Description Set Up'),
            _(u'Description Roles and responsibilities'),
            _(u'Description Meeting processes'),
            _(u'Description Work processes'),
            _(u'Description Communication and transparency'),
            _(u'Description Trust and teamwork'),
            _(u'Description Partnership adaptation and sustainability'),
            _(u'Description Resourses'),
        ]
        tool_ts = getToolByName(self, 'translation_service')
        portal = api.portal.get()
        num = 0
        for item in titles:
            title_es = tool_ts.translate(item, domain='gwopa', target_language='es')
            title_fr = tool_ts.translate(item, domain='gwopa', target_language='fr')
            description_en = tool_ts.translate(descriptions[num], domain='gwopa', target_language='en')
            description_es = tool_ts.translate(descriptions[num], domain='gwopa', target_language='es')
            description_fr = tool_ts.translate(descriptions[num], domain='gwopa', target_language='fr')
            num = num + 1

            api.content.create(
                type='PartnershipPractice',
                title=item,
                title_es=title_es if title_es != '' else title_en,
                title_fr=title_fr if title_fr != '' else title_en,
                description=description_en,
                description_es=description_es if description_es != '' else description_en,
                description_fr=description_fr if description_fr != '' else description_en,
                container=portal.config.partnershippractice,
                safe_id=True)