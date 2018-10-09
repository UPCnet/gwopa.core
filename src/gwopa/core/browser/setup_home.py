# -*- coding: utf-8 -*-
from five import grok
from plone import api
from cgi import parse_qs
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from plone.app.multilingual.browser.setup import SetupMultilingualSite
from plone.app.multilingual.interfaces import ITranslationManager
import logging
from gwopa.core.interfaces import IGwopaCoreLayer
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from zope.component import getUtility
from plone.registry.interfaces import IRegistry


grok.templatedir("templates")

NEWS_QUERY = [{'i': u'portal_type', 'o': u'plone.app.querystring.operation.selection.is', 'v': [u'News Item', u'Link']},
              {'i': u'review_state', 'o': u'plone.app.querystring.operation.selection.is', 'v': [u'published']},
              {'i': u'path', 'o': u'plone.app.querystring.operation.string.relativePath', 'v': u'..'}]
QUERY_SORT_ON = u'effective'
EVENT_QUERY = [{'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['Event']},
               {'i': 'start', 'o': 'plone.app.querystring.operation.date.afterToday', 'v': ''},
               {'i': 'review_state', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['published']}]


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
                self.setup_multilingual()
                self.createContent()
                self.request.response.redirect(self.context.absolute_url())

    def contentStatus(self):
        objects = [(u'Homepage', [('homepage', 'en'), ('homepage', 'es'), ('homepage', 'fr')]),
                   ]

        result = []
        portal = api.portal.get()

        for o in objects:
            tr = [o[0]]
            for td, lang in o[1]:
                if lang == 'root':
                    tr.append(getattr(portal, td, False) and 'Created' or 'Missing')
                else:
                    if getattr(portal, lang, False):
                        tr.append(getattr(portal[lang], td, False) and 'Created' or 'Missing')
                    else:
                        tr.append('Missing')
            result.append(tr)
        return result

    def apply_default_language_settings(self):
        pl = api.portal.get_tool('portal_languages')
        pl.removeSupportedLanguages(pl.getSupportedLanguages())
        pl.addSupportedLanguage('en')
        pl.addSupportedLanguage('es')
        pl.addSupportedLanguage('fr')
        pl.setDefaultLanguage('en')

    def setup_multilingual(self):
        setupTool = SetupMultilingualSite()
        self.context.setLanguage('en')
        portal = api.portal.get()
        try:
            api.content.delete(obj=portal['en-us'])
        except:
            pass
        setupTool.setupSite(self.context, False)

    def createContent(self):
        """ Method that creates all the default content """
        portal = api.portal.get()
        portal_en = portal['en']

        # Get rid of the original page
        if getattr(portal_en, 'front-page', False):
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
        # portal_en.setLayout('homepage')

        return True

    def link_translations(self, items):
        """
        Links the translations with the declared items with the form:
        [(obj1, lang1), (obj2, lang2), ...] assuming that the first element
        is the 'canonical' (in PAM there is no such thing).
        """
        # Grab the first item object and get its canonical handler
        canonical = ITranslationManager(items[0][0])

        for obj, language in items:
            if not canonical.has_translation(language):
                canonical.register_translation(language, obj)

    def constrain_content_types(self, container, content_types):
        # Set on them the allowable content types
        behavior = ISelectableConstrainTypes(container)
        behavior.setConstrainTypesMode(1)
        behavior.setLocallyAllowedTypes(content_types)
        behavior.setImmediatelyAddableTypes(content_types)

    def clone_collection_settings(self, origin, target):
        if getattr(origin, 'query', False):
            target.query = origin.query
        if getattr(origin, 'sort_on', False):
            target.sort_on = origin.sort_on
        if getattr(origin, 'sort_reversed', False):
            target.sort_reversed = origin.sort_reversed
        if getattr(origin, 'limit', False):
            target.limit = origin.limit
        if getattr(origin, 'item_count', False):
            target.item_count = origin.item_count
        if getattr(origin, 'customViewFields', False):
            target.customViewFields = origin.customViewFields
