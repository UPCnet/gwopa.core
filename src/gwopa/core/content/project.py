# -*- coding: utf-8 -*-
from five import grok
from plone import api
from plone.supermodel import model
from zope import schema
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from plone.app.textfield import RichText
from zope.interface import Invalid
from zope.interface import invariant
from plone.namedfile import field as namedfile
from gwopa.core import _
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
import unicodedata
from zope.schema.vocabulary import SimpleTerm
import pycountry
import datetime

grok.templatedir("templates")


def vocabulary_maker(l):
    vocab_list = []
    for row in l:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode('ascii', errors='ignore').decode('ascii'), title=_(row))
        vocab_list.append(entry)
    return SimpleVocabulary(vocab_list)


countries = vocabulary_maker([country.name for country in pycountry.countries])


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def default_today(context):
    """Provide default start for the form.
    """
    return datetime.date.today()


@provider(IContextAwareDefaultFactory)
def default_tomorrow(context):
    """Provide default start for the form.
    """
    return datetime.date.today() + datetime.timedelta(1)


def PartnersList(self):
    values = api.portal.get_registry_record(
        'gwopa.core.controlpanel.IGWOPASettings.partners_list')
    terms = []
    for item in values:
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)


directlyProvides(PartnersList, IContextSourceBinder)


def WOPList(self):
    values = api.portal.get_registry_record(
        'gwopa.core.controlpanel.IGWOPASettings.wop_list')
    terms = []
    for item in values:
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)


directlyProvides(WOPList, IContextSourceBinder)


def ImprovementAreaList(context):
    """ Create vocabulary """
    terms = []
    values = api.content.find(portal_type="ImprovementArea")
    for item in values:
        item = item.Title
        if isinstance(item, str):
            flattened = unicodedata.normalize('NFKD', item.decode('utf-8')).encode('ascii', errors='ignore')
        else:
            flattened = unicodedata.normalize('NFKD', item).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item, flattened, item))

    return SimpleVocabulary(terms)


directlyProvides(ImprovementAreaList, IContextSourceBinder)


class IProject(model.Schema):
    """  Project type
    """
    title = schema.TextLine(
        title=_(u"Project name"),
        description=_(u"Add the project title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Project Image'),
        required=False,
    )

    start = schema.Date(
        title=_(u'Start date'),
        description=_(u'Date when the project begins.'),
        required=True,
        defaultFactory=default_today
    )

    end = schema.Date(
        title=_(u'End date'),
        description=_(u'Date when the project ends.'),
        required=True,
        defaultFactory=default_tomorrow
    )

    geolocation = schema.Choice(
        title=_(u"Geolocation"),
        description=_(u"Select country"),
        vocabulary=countries,
        required=True,
    )

    latitude = schema.Text(
        title=_(u"latitude"),
    )

    longitude = schema.Text(
        title=_(u"longitude"),
    )

    # Partners are in gwopa controlpanel
    partners = schema.List(
        title=_(u"Partners"),
        description=_(u"Partner/partners associated to this project"),
        required=False,
        value_type=schema.Choice(
            source=PartnersList,
        ),
    )

    project_manager = schema.TextLine(
        title=_(u"Project Manager"),
        description=_(u""),
        required=False,
    )

    # area = schema.List(
    #     title=_(u"Interest Areas"),
    #     description=_(u""),
    #     value_type=schema.Choice(
    #         source=ImprovementAreaList,
    #     ),
    #     required=False,
    # )

    # it_members = schema.TextLine(
    #     title=_(u"Improvement track team and members"),
    #     description=_(u""),
    #     required=False,
    # )

    budget = schema.Int(
        title=_(u"Budget"),
        required=False,
    )

    contribution = RichText(
        title=_(u"Contribution by partners and donors"),
        description=_(u""),
        required=False,
    )

    # WOPS are in gwopa controlpanel
    wop_program = schema.List(
        title=_(u"WOP Program"),
        description=_(u"Program/programs associated to this project"),
        value_type=schema.Choice(
            source=WOPList,
        ),
        required=False,
    )

    risks = schema.Text(
        title=_(u'Risks'),
        required=False,
        missing_value=u'',
    )

    assumptions = schema.Text(
        title=_(u'Assumptions'),
        required=False,
        missing_value=u'',
    )

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(u"End date must be after start date.")


class View(grok.View):
    grok.context(IProject)
    grok.template('project_view')

    def getArea(self):
        values = self.context.area
        results = ''
        if values:
            if len(values) == 1:
                return values[0]
            else:
                for value in values:
                    results = str(results) + str(value) + str(', ')
        else:
            return None

        return results[:-2]  # Removes latest comma
