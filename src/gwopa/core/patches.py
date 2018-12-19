# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IJsonCompatible
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
import six
from zope.interface import implements
from plone.i18n.interfaces import INegotiateLanguage
from Products.CMFPlone.interfaces import ILanguageSchema
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone import api

from plone.restapi.serializer.converters import default_converter


@adapter(Interface)
@implementer(IJsonCompatible)
def default_converter_modified(value):
    if value is None:
        return value

    if type(value) in (six.text_type, bool, int, float, int):
        return value
    # Monkeypatched to check geolocation values and return in JSON format
    if type(value).__name__ == 'Geolocation':
        return 'Latitude: ' + str(value.latitude) + ' / ' + 'Longitude: ' + str(value.longitude)

    raise TypeError(
        'No converter for making'
        ' {0!r} ({1}) JSON compatible.'.format(value, type(value)))


default_converter.func_code = default_converter_modified.func_code


class NegotiateLanguage(object):
    """Perform default language negotiation"""
    implements(INegotiateLanguage)

    def __init__(self, site, request):
        """Setup the current language stuff."""
        registry = getUtility(IRegistry)
        lan_tool = registry.forInterface(ILanguageSchema, prefix='plone')
        tool = api.portal.get_tool('portal_languages')
        langs = []
        useContent = lan_tool.use_content_negotiation
        useCcTLD = lan_tool.use_cctld_negotiation
        useSubdomain = lan_tool.use_subdomain_negotiation
        usePath = lan_tool.use_path_negotiation
        useCookie = lan_tool.use_cookie_negotiation
        setCookieEverywhere = lan_tool.set_cookie_always
        authOnly = lan_tool.authenticated_users_only
        useRequest = lan_tool.use_request_negotiation
        useDefault = 1  # This should never be disabled
        langsCookie = None

        if usePath:
            # This one is set if there is an allowed language in the current path
            langs.append(tool.getPathLanguage())

        if useContent:
            langs.append(tool.getContentLanguage())

        if useCookie and not (authOnly and tool.isAnonymousUser()):
            # If we are using the cookie stuff we provide the setter here
            set_language = request.get('set_language', None)
            if set_language:
                langsCookie = tool.setLanguageCookie(
                    set_language,
                    request=request
                )
            else:
                # Get from cookie
                langsCookie = tool.getLanguageCookie(request)
            langs.append(langsCookie)

        if useSubdomain:
            langs.extend(tool.getSubdomainLanguages())

        if useCcTLD:
            langs.extend(tool.getCcTLDLanguages())

        # Get langs from request
        if useRequest:
            langs.extend(tool.getRequestLanguages())

        # Get default
        if useDefault:
            langs.append(tool.getDefaultLanguage())

        # Filter None languages
        langs = [lang for lang in langs if lang is not None]

        # Set cookie language to language
        if setCookieEverywhere and useCookie and langs[0] != langsCookie:
            tool.setLanguageCookie(langs[0], noredir=True)

        self.default_language = langs[-1]
        self.language = langs[0]
        self.language_list = langs[1:-1]

        if useCookie:
            # Patched to meet the feature requirements for the client
            custom_lang_cookie = request.cookies.get('I18N_LANGUAGE')
            if custom_lang_cookie:
                self.language = custom_lang_cookie
