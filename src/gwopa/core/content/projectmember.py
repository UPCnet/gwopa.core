# -*- coding: utf-8 -*-
import unicodedata
import pycountry
from five import grok
from plone.supermodel import model
from zope import schema
from plone.namedfile import field as namedfile
from gwopa.core import _
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

grok.templatedir("templates")


def vocabulary_maker(l):
    vocab_list = []
    for row in l:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode('ascii', errors='ignore').decode('ascii'), title=_(row))
        vocab_list.append(entry)
    return SimpleVocabulary(vocab_list)


countries = vocabulary_maker([country.name for country in pycountry.countries])


class IProjectmember(model.Schema):
    """  Project  Membertype
    """
    title = schema.TextLine(
        title=_(u"Username"),
        description=_(u"The Member Name and Surname"),
        required=False,
    )

    image = namedfile.NamedBlobImage(
        title=_(u'member_image', default=u'Member profile picture'),
        description=u'',
        required=False,
    )

    country = schema.Choice(
        title=_(u'Country'),
        description=_(u"Select country"),
        vocabulary=countries,
        required=True,
    )

    year = schema.TextLine(
        title=_(u"Year"),
        description=_(u"Indicate the year of..."),
        required=False,
    )


class View(grok.View):
    grok.context(IProjectmember)
    grok.template('projectmember_view')
