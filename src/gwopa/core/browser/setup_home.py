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
import random
from Products.statusmessages.interfaces import IStatusMessage
from gwopa.core import _
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.formwidget.geolocation.geolocation import Geolocation
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from plone.app.dexterity.behaviors import constrains

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

        try:
            properties = dict(
                fullname='Test',
                location='USer1',
            )
            api.user.create(
                username='user1',
                email='user1@test.com',
                password='user1',
                properties=properties,
            )
        except:
            pass

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
                title='Working Areas Items',
                description='Working Areas used in the projects',
                container=config_folder,
                safe_id=False)
            allowed_types = ['ItemArea', ]
            _setup_constrains(areas, allowed_types)
            outcomes = api.content.create(
                type='Folder',
                id='capacitychanges',
                title='Capacity Changes Values',
                description='Values used in Outcome CC and CCS',
                container=config_folder,
                safe_id=False)
            allowed_types = ['OutcomeCCItem', ]
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
            message = _(u"The default config has been applied.")
            messages.addStatusMessage(message, type="info")
        except Exception, e:
            # Show friendly error message
            messages.addStatusMessage(unicode(e), 'error')

    def createDemoContent(self):
        """ Assign default values to panel control options """
        portal = api.portal.get()
        settingspage = api.content.create(
            type='SettingsPage',
            id='settings',
            title='GWOPA Settings Page',
            description='GWOPA default values used in Site',
            container=portal.config,
            safe_id=False)
        settingspage.currency = 'Dollars\nEuros\nPounds'
        settingspage.measuring_unit = 'liters\nm3\npeople\nothers'
        settingspage.measuring_frequency = 'quarterly\nbiannually\nannually'
        # Create demo Platforms
        p1 = api.content.create(
            type='Platform',
            id='platform1',
            title='WOP Platform 1',
            description='WOP Platform 1',
            container=portal.config.platforms,
            safe_id=False)
        p1.country = ['Spain']
        p2 = api.content.create(
            type='Platform',
            id='platform2',
            title='WOP Platform 2',
            description='WOP Platform 2',
            container=portal.config.platforms,
            safe_id=False)
        p2.country = ['Spain']
        p3 = api.content.create(
            type='Platform',
            id='platform3',
            title='WOP Platform 3',
            description='WOP Platform 3',
            container=portal.config.platforms,
            safe_id=False)
        p3.country = ['Spain']
        p4 = api.content.create(
            type='Platform',
            id='platform4',
            title='WOP Platform 4',
            description='WOP Platform 4',
            container=portal.config.platforms,
            safe_id=False)
        p4.country = ['Spain']
        p5 = api.content.create(
            type='Platform',
            id='platform5',
            title='WOP Platform 5',
            description='WOP Platform 5',
            container=portal.config.platforms,
            safe_id=False)
        p5.country = ['Spain']

        # Create demo programs
        portal = api.portal.get()
        p1 = api.content.create(
            type='Program',
            id='program1',
            title='WOP Program 1',
            description='WOP Program 1',
            container=portal.config.programs,
            safe_id=False)
        p1.contact = 'userprogram1@test.com'
        p1.country = ['Spain']
        p2 = api.content.create(
            type='Program',
            id='program2',
            title='WOP Program 2',
            description='WOP Program 2',
            container=portal.config.programs,
            safe_id=False)
        p2.contact = 'userprogram2@test.com'
        p2.country = ['Spain']
        p3 = api.content.create(
            type='Program',
            id='program3',
            title='WOP Program 3',
            description='WOP Program 3',
            container=portal.config.programs,
            safe_id=False)
        p3.contact = 'userprogram3@test.com'
        p3.country = ['Spain']
        p4 = api.content.create(
            type='Program',
            id='program4',
            title='WOP Program 4',
            description='WOP Program 4',
            container=portal.config.programs,
            safe_id=False)
        p4.contact = 'userprogram4@test.com'
        p4.country = ['Spain']
        p5 = api.content.create(
            type='Program',
            id='program5',
            title='WOP Program 5',
            description='WOP Program 5',
            container=portal.config.programs,
            safe_id=False)
        p5.contact = 'userprogram5@test.com'
        p5.country = ['Spain']

        # Create demo partners
        portal = api.portal.get()
        p1 = api.content.create(
            type='Partner',
            id='partner1',
            title='WOP Partner 1',
            description='WOP Partner 1',
            container=portal.config.partners,
            safe_id=False)
        p1.contact = 'userpartner1@test.com'
        p1.country = ['Spain']
        geo = IGeolocatable(p1, None)
        geo.geolocation = Geolocation(41.3828939, 2.1774322)
        p2 = api.content.create(
            type='Partner',
            id='partner2',
            title='WOP Partner 2',
            description='WOP Partner 2',
            container=portal.config.partners,
            safe_id=False)
        p2.contact = 'userpartner2@test.com'
        p2.country = ['Spain']
        geo = IGeolocatable(p2, None)
        geo.geolocation = Geolocation(41.3828939, 2.1774322)
        p3 = api.content.create(
            type='Partner',
            id='partner3',
            title='WOP Partner 3',
            description='WOP Partner 3',
            container=portal.config.partners,
            safe_id=False)
        p3.contact = 'userpartner3@test.com'
        p3.country = ['Spain']
        geo = IGeolocatable(p3, None)
        geo.geolocation = Geolocation(41.3828939, 2.1774322)
        p4 = api.content.create(
            type='Partner',
            id='partner4',
            title='WOP Partner 4',
            description='WOP Partner 4',
            container=portal.config.partners,
            safe_id=False)
        p4.contact = 'userpartner4@test.com'
        p4.country = ['Spain']
        geo = IGeolocatable(p4, None)
        geo.geolocation = Geolocation(41.3828939, 2.1774322)
        p5 = api.content.create(
            type='Partner',
            id='partner5',
            title='WOP Partner 5',
            description='WOP Partner 5',
            container=portal.config.partners,
            safe_id=False)
        p5.contact = 'userpartner5@test.com'
        p5.country = ['Spain']
        geo = IGeolocatable(p5, None)
        geo.geolocation = Geolocation(41.3828939, 2.1774322)
        # Create base Outcome CC selectable Values
        api.content.create(
            type='OutcomeCCItem',
            title='Mission & Strategy',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Leadership',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Organizational culture',
            icon='fas fa-university',
            category='Organizational transformational dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Others',
            icon='fab fa-industry',
            category='Organizational transformational dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Organizational structure',
            icon='fas fa-sitemap',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Management practices',
            icon='fas fa-comments',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Systems',
            icon='fas fa-map',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Infrastructure',
            icon='fas fa-tree',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Equipment',
            icon='fas fa-university',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Updated knowledge on conditions of systems & infrastructure',
            icon='fas fa-tree',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Working routines',
            icon='fas fa-cogs',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Others',
            icon='fab fa-industry',
            category='Organizational transactional dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Motivation',
            icon='fas fa-users',
            category='Individual dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Fit between skill & Knowledge and tasks to perform',
            icon='fas fa-building',
            category='Individual dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Applied new skills & knowledge',
            icon='fas fa-search',
            category='Individual dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)
        api.content.create(
            type='OutcomeCCItem',
            title='Others',
            icon='fab fa-industry',
            category='Individual dimensions',
            container=portal.config.capacitychanges,
            safe_id=True)

        # Create demo programs
        portal = api.portal.get()
        api.content.create(
            type='ItemArea',
            id='area1',
            title='Working Area 1',
            container=portal.config.areas,
            safe_id=True)
        api.content.create(
            type='ItemArea',
            id='area2',
            title='Working Area 2',
            container=portal.config.areas,
            safe_id=True)
        api.content.create(
            type='ItemArea',
            id='area3',
            title='Working Area 3',
            container=portal.config.areas,
            safe_id=True)
        api.content.create(
            type='ItemArea',
            id='area4',
            title='Working Area 4',
            container=portal.config.areas,
            safe_id=True)
        api.content.create(
            type='ItemArea',
            id='area5',
            title='Working Area 5',
            container=portal.config.areas,
            safe_id=True)

        self.createProjects(5)
        return "Demo content created"

    def getRandomImage(self, w, h):
        """ Valid topics keys:
                abstract, city, people, transport, animals, food, nature
                business, nightlife, sports, cats, fashion, technics

                    https://dummyimage.com/600x400/eaeaea/aeaeae
                    http://lorempixel.com/

        """
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
                safe_id=True)
            project.image = self.getRandomImage(200, 200)
            project.description = self.getLoremIpsum(1, 'medium', 'plaintext')
            project.budget = random.randint(1, 101)
            project.contribution = RichTextValue(
                self.getLoremIpsum(2, 'long', 'html'),
                'text/html', 'text/html')
            new_value = []
            project.partners = new_value
            geo = IGeolocatable(project, None)
            geo.geolocation = Geolocation(41.3828939, 2.1774322)
            project.assumptions = project.contribution
            project.objectives = project.contribution
            project.country = 'Spain'
