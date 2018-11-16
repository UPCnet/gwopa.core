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
from requests.exceptions import ConnectionError
requests.packages.urllib3.disable_warnings()

grok.templatedir("templates")


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
                message = _(u"The default config has been applied.")
                IStatusMessage(self.request).addStatusMessage(message, type="info")
                # self.request.response.redirect(self.context.absolute_url())
            if 'createdemocontent' in query:
                logger = logging.getLogger('# Creating DEMO CONTENT on Site ->')
                logger.info('%s' % self.context.id)
                self.createDemoContent()
                message = _(u"Demo content has been created.")
                IStatusMessage(self.request).addStatusMessage(message, type="info")
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
            api.content.delete(obj=portal['front-page'])

        # Hide 'Members', 'news' and 'events' folders
        if getattr(portal, 'Members', False):
            api.content.delete(obj=portal['Members'])
        if getattr(portal, 'news', False):
            api.content.delete(obj=portal['news'])
        if getattr(portal, 'events', False):
            api.content.delete(obj=portal['events'])

        # Set the default pages to the homepage view
        portal.setLayout('homepage')
        try:
            config_folder = api.content.create(
                type='Folder',
                id='config',
                title='Config folder',
                Description='This folder will hold configuration folders used by the Site and managed by the administrators',
                container=portal,
                safe_id=False)
            api.content.create(
                type='Folder',
                id='regions',
                title='Regions',
                description='Regions used as user registration field',
                container=config_folder,
                safe_id=False)
            config_folder = api.content.create(
                type='Folder',
                id='projects',
                title='Projects',
                Description='Projects of the Site',
                container=portal,
                safe_id=False)
        except Exception:
                pass
        return True

    def createDemoContent(self):
        """ Assign default values to panel control options """
        # WOP LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.wop_list')
        if not current or current[0] is '':
            current = []
        default_wop_list = [
            u'WOP Program Demo List 1',
            u'WOP Program Demo List 2',
            u'WOP Program Demo List 3',
            u'WOP Program Demo List 4',
            u'WOP Program Demo List 5']
        new_values = current + default_wop_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.wop_list', sorted(list(set(new_values))))
        # Partners LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.partners_list')
        if not current or current[0] is '':
            current = []
        default_partners_list = [
            u'Partner Demo User 1',
            u'Partner Demo User 2',
            u'Partner Demo User 3',
            u'Partner Demo User 4',
            u'Partner Demo User 5']
        new_values = current + default_partners_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.partners_list', sorted(list(set(new_values))))
        # Currency LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.currency')
        if not current or current[0] is '':
            current = []
        default_currency_list = [
            u'$ - Dollars',
            u'€ - Euros',
            u'£ - Pounds']
        new_values = current + default_currency_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.currency', sorted(list(set(new_values))))
        # Measuring units LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.measuring_unit')
        if not current or current[0] is '':
            current = []
        default_measuring_list = [
            u'liters',
            u'm3',
            u'people',
            u'others',
        ]
        new_values = current + default_measuring_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.measuring_unit', sorted(list(set(new_values))))
        # Measuring frequency LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.measuring_frequency')
        if not current or current[0] is '':
            current = []
        default_measuringfreq_list = [
            u'quarterly',
            u'biannually',
            u'annually',
        ]
        new_values = current + default_measuringfreq_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.measuring_frequency', sorted(list(set(new_values))))
        #  Regions LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.region_list')
        if not current or current[0] is '':
            current = []
        default_region_list = [
            u'Europe',
            u'Africa',
            u'America',
        ]
        new_values = current + default_region_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.region_list', sorted(list(set(new_values))))
        #  wop_platform LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.wop_platform')
        if not current or current[0] is '':
            current = []
        default_wop_platform_list = [
            u'WOP Platform 1',
            u'WOP Platform 2',
            u'WOP Platform 3',
            u'WOP Platform 4',
            u'WOP Platform 5',
        ]
        new_values = current + default_wop_platform_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.wop_platform', sorted(list(set(new_values))))
        #  experimental areas LIST
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.experimental_areas')
        if not current or current[0] is '':
            current = []
        default_experimental_areas_list = [
            u'Experimental Area 1',
            u'Experimental Area 2',
            u'Experimental Area 3',
            u'Experimental Area 4',
            u'Experimental Area 5',
        ]
        new_values = current + default_experimental_areas_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.experimental_areas', sorted(list(set(new_values))))

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
            data = requests.get('http://dummyimage.com/{0}x{1}/aeaeae/ffffff'.format(w, h), verify=False, timeout=10).content
        except ConnectionError:
            data = requests.get(api.portal.get().absolute_url() + '/++theme++gwopa.theme/assets/images/empty200.png', verify=False, timeout=10).content

        image = NamedBlobImage(data=data,
                               filename=u'image.jpg',
                               contentType='image/jpeg')
        return image

    def getLoremIpsum(self, number, length, type_code):
        """ Returns Lorem Ipsum text
        """
        try:
            text = requests.get('http://loripsum.net/api/{0}/{1}/{2}'.format(number, type_code, length), verify=False, timeout=10).content
        except ConnectionError:
            return "</ Empty field because no network response from http://loripsum.net />"
        return text

    def createProjects(self, number):
        portal = api.portal.get()
        wops = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.wop_list')
        partners = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.partners_list')
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
            wop_item = wops[i]
            new_value = []
            new_value.append(wop_item)
            project.wop_program = new_value
            partner_item = partners[i]
            new_value = []
            new_value.append(partner_item)
            project.partners = new_value
            project.latitude = 41.3828939
            project.longitude = 2.1774322
            project.risks = project.contribution
            project.assumptions = project.contribution
            project.objectives = project.contribution
            project.country = 'Spain'
