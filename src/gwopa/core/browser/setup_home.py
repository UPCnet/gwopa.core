# -*- coding: utf-8 -*-
from five import grok
from plone import api
from cgi import parse_qs
from Products.CMFPlone.interfaces import IPloneSiteRoot
import logging
from gwopa.core.interfaces import IGwopaCoreLayer
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
import requests
from plone.namedfile.file import NamedBlobImage
from plone.app.textfield.value import RichTextValue
import random
import transaction

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
                logger = logging.getLogger('Executed setup_home on Site ->')
                logger.info('%s' % self.context.id)
                self.apply_default_language_settings()
                self.createContent()
                self.request.response.redirect(self.context.absolute_url())
            if 'createdemocontent' in query:
                logger = logging.getLogger('Creating DEMO CONTENT on Site ->')
                logger.info('%s' % self.context.id)
                self.createDemoContent()
                self.request.response.redirect(self.context.absolute_url())

    def apply_default_language_settings(self):
        pl = api.portal.get_tool('portal_languages')
        pl.removeSupportedLanguages(pl.getSupportedLanguages())
        pl.addSupportedLanguage('en')
        pl.addSupportedLanguage('es')
        pl.addSupportedLanguage('fr')
        pl.setDefaultLanguage('en')

    def createContent(self):
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

        # Set toolbar top
        pc = api.portal.get_tool('portal_catalog')
        pc.clearFindAndRebuild()
        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(
            ISiteSchema,
            prefix='plone',
            check=False
        )
        site_settings.toolbar_position == 'top'

        # Set the default pages to the homepage view
        portal.setLayout('homepage')

        return True

    def createDemoContent(self):
        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.wop_list')
        if not current:
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

        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.partners_list')
        if not current:
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

        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.measuring_unit')
        if not current:
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

        current = api.portal.get_registry_record('gwopa.core.controlpanel.IGWOPASettings.measuring_frequency')
        if not current:
            current = []
        default_measuringfreq_list = [
            u'quarterly',
            u'biannually',
            u'annually',
        ]
        new_values = current + default_measuringfreq_list
        api.portal.set_registry_record(
            'gwopa.core.controlpanel.IGWOPASettings.measuring_frequency', sorted(list(set(new_values))))

        self.createProjects(5)
        return "Demo content created"

    def getRandomImage(self, w, h):
        """ Valid topics keys:
                abstract, city, people, transport, animals, food, nature
                business, nightlife, sports, cats, fashion, technics

                    https://dummyimage.com/600x400/eaeaea/aeaeae
                    http://lorempixel.com/

        """
        data = requests.get('http://dummyimage.com/{0}x{1}/aeaeae/ffffff'.format(w, h), verify=False, timeout=10).content
        image = NamedBlobImage(data=data,
                               filename=u'image.jpg',
                               contentType='image/jpeg')
        return image

    def getLoremIpsum(self, number, length, type_code):
        """ Returns Lorem Ipsum text
        """
        text = requests.get('http://loripsum.net/api/{0}/{1}/{2}'.format(number, type_code, length), verify=False, timeout=10).content
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
                container=portal,
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
            # from plone.formwidget.geolocation.interfaces import IGeolocation
            # import ipdb; ipdb.set_trace()
            # value = IGeolocation.providedBy(project)
            # project.geolocation.latitude = 0.0
            # project.geolocation.longitude = 0.0

            partner_item = partners[i]
            new_value = []
            new_value.append(partner_item)
            project.partners = new_value
