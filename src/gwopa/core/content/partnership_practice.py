# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from five import grok
from plone import api
from plone.app.event.base import construct_calendar
from plone.app.event.base import first_weekday
from plone.app.event.base import localized_today
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile import field as namedfile
from zope import schema
from zope.i18nmessageid import MessageFactory

from gwopa.core import _
from gwopa.core import utils

import calendar

PLMF = MessageFactory('plonelocales')


grok.templatedir("templates")


class IPartnershipPractice(form.Schema):
    """  Partnership Practice type
    """
    title = schema.TextLine(
        title=_(u"Title English"),
        required=True,
    )

    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=False,
    )

    title_fr = schema.TextLine(
        title=_(u"Title French"),
        required=False,
    )

    description = schema.TextLine(
        title=_(u"Description English"),
        required=True,
        missing_value=u'',
    )

    description_es = schema.TextLine(
        title=_(u"Description Spanish"),
        required=False,
        missing_value=u'',
    )

    description_fr = schema.TextLine(
        title=_(u"Description French"),
        required=False,
        missing_value=u'',
    )


# @indexer(IPartnershipPractice)
# def title_es(context):
#     try:
#         value = context.title_es.decode("utf-8")
#         return value
#     except:
#         return context.title_es


# grok.global_adapter(title_es, name='title_es')


# @indexer(IPartnershipPractice)
# def title_fr(context):
#     try:
#         value = context.title_fr.decode("utf-8")
#         return value
#     except:
#         return context.title_fr


# grok.global_adapter(title_fr, name='title_fr')

# @indexer(IPartnershipPractice)
# def description_es(context):
#     try:
#         value = context.description_es.decode("utf-8")
#         return value
#     except:
#         return context.description_es


# grok.global_adapter(description_es, name='description_es')


# @indexer(IPartnershipPractice)
# def description_fr(context):
#     try:
#         value = context.description_fr.decode("utf-8")
#         return value
#     except:
#         return context.description_fr


# grok.global_adapter(description_fr, name='description_fr')

class Edit(form.SchemaEditForm):
    grok.context(IPartnershipPractice)


class View(grok.View):
    grok.context(IPartnershipPractice)
    grok.template('partnershippractice_view')
    grok.require('zope2.View')