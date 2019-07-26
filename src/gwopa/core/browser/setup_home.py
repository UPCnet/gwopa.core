# -*- coding: utf-8 -*-
from five import grok
from plone import api
from cgi import parse_qs
from Products.CMFPlone.interfaces import IPloneSiteRoot
import logging
from gwopa.core.interfaces import IGwopaCoreLayer
import requests
from plone.namedfile.file import NamedBlobImage
from plone.app.textfield.value import RichTextValue
from Products.statusmessages.interfaces import IStatusMessage
from gwopa.core import _
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from plone.app.dexterity.behaviors import constrains
from random import random
import math
from gwopa.core.content.project import default_plus_one_year, default_today

from requests.exceptions import ConnectionError
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

            outputs = api.content.create(
                type='Folder',
                id='outputs',
                title='Default Output values',
                description='Default title outputs used in projects',
                container=config_folder,
                safe_id=False)
            allowed_types = ['Outputdefaults', ]
            _setup_constrains(outputs, allowed_types)

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

            message = _(u"The default config has been applied.")
            messages.addStatusMessage(message, type="info")
        except Exception, e:
            # Show friendly error message
            messages.addStatusMessage(unicode(e), 'error')

    def createDemoContent(self):
        """ Assign default values to panel control options """
        for i in xrange(1, 6):
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
            title='GWOPA Settings Page',
            description='GWOPA default values used in Site',
            container=portal.config,
            safe_id=False)
        settingspage.currency = 'USD-US Dollar-$\r\nEUR-Euro-€\r\nGBP-British Pound-£\r\nAUD-Australian Dollar-$\r\nCAD-Canadian Dollar-$'
        settingspage.measuring_unit = 'liters\nm3\npeople\nothers'
        settingspage.measuring_frequency = 'Annually,1\nBiannually,2\nQuarterly,4'
        settingspage.degree_changes = '-2 Very negative\n-1 Negative\n0 No change\n1 Positive\n2 Very positive'
        settingspage.contributed_project = '0 No contribution\n1 Fair contribution\n2 Very high contribution'
        settingspage.consensus = 'One Partner\nWop Partners'

        portal = api.portal.get()

        # Create demo Platforms
        wop_platforms = [
            "Cari-WOP",
            "PWWA",
            "Waterlinks",
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

        # Create base Outcome CC selectable Values
        api.content.create(
            type='OutcomeCCItem',
            title='Mission & Strategy',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Leadership',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Organizational culture',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='External resources',
            icon='fab fa-industry',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Network / External relations',
            icon='fas fa-sitemap',
            category='Organizational transformational dimensions',
            short_category='transformational',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Systems',
            icon='fas fa-map',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Structure',
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Management',
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Information',
            icon='fas fa-tree',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Infrastructure / Equipment',
            icon='fas fa-university',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Working routines',
            icon='fas fa-cogs',
            category='Organizational transactional dimensions',
            short_category='transactional',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Knowledge & Skills',
            icon='fab fa-industry',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Motivation',
            icon='fas fa-users',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Applied knowledge skills',
            icon='fas fa-search',
            category='Individual dimensions',
            short_category='individual',
            container=portal.config.capacitychanges,
            safe_id=True)

        # Create item areas
        working_areas = [
            'Asset Management',
            'Billing & Collection Efficiency',
            'Business Planning',
            'Commercial & Physical Losses - NRW',
            'Customer Service',
            'Financial Management',
            'Wastewater Collection & Treatment',
            'Production processes  & Service Quality & Water Safety  (Drinking Water)',
            'Operation & Maintenance',
            'Energy Efficiency',
            'Human Resource Management/ Organizational Development',
            'Corporate Governance & Institutions',
            'Catchment Management / IWRM',
            'Climate Change Resilience',
            'Services in Low-Income Areas',
            'Extension of Sanitation & Hygiene services ',
            'Extension of Water Supply Services ',
            'Social Inclusion/Gender  ',
            'Information & Technology',
            'Policy and Legal Support ',
            'Water Demand Management',
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
            'Leadership development program prepared',
            'Business plan developed/improved',
            'Management information system introduced/improved',
            'Internal audit performed on transparency and integrity',
            'Improvement plan drawn up based on internal audit',
            'Yearly benchmark report prepared',
            'Organisation improvement plan developed',
            'Capacity development program prepared',
            'NRW reduction plan developed',
            'Number of people trained in NRW reduction approach',
            'Maintenance and management program developed',
            'Number of people trained in maintenance and management',
            'Development of an improvement plan for sanitation, sewage and waste water treatment',
            'Pro-poor coordinators appointed and trained',
            'Pro-poor vision, strategy and objectives developed',
            'Proposals developed for providing people with direct acces to improved water and/ or sanitation facilities',
            'Coordination of the implementation of the proposals',
            'Climate resistant water supply program 2050 developed',
            'Energy saving program developed',
            'Gender analysis and approach developed'
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
            'Total number of connections',
            'Total number of people served',
            'Coverage',
            '(Estimated) coverage LIA population',
            '% Female employees',
            '% Female employees in management positions',
            'Number of FT employees per 1000 active connections',
            'NRW in m3 per actve connection per year',
            'NRW as percentage of system input',
            'Collection efficiency',
            'Customer satisfaction',
            'Working ratio',
            'Operating ratio',
            'Debt service coverage ratio (DSCR)',
            'Energy consumption per m3 system input',
            'Expenditures on chemicals per m3 system input',
            'Chlorine consumption per m3 system input',
            'Aluminium sulphate consumption per m3 system input',
            'Percentage of required checks carried out for faecal coliform',
            'Percentage of checks that do not comply with norm on faecal coliform',
            'Percentage of required checks carried out for residual chlorine',
            'Percentage of checks that do not comply with norm on residual Chlorine',
            'Number of people with access to improved sanitation facilities',
            'Percentage of people with access to improved sanitation facilities',
            'Number of people with access to unimproved sanitation facilities',
            'Percentage of people with access to unimproved sanitation facilities',
            'Total number of sewerage connections',
            'Percentage of waste water treated',
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
            'Internal organizational',
            'External environment',
            'WOP project - related',
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
            'Internal organizational',
            'External environment',
            'WOP project - related',
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
        for i in xrange(1, 6):
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
            "Waterlinks",
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
            'Porcentaje de personas con acceso a instalaciones sanitarias mejoradas.',
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
            'IOrganizacion interna',
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
