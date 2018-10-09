# -*- coding: utf-8 -*-
from five import grok
from plone import api
from plone.supermodel import model
from zope import schema
from plone.app.event.base import default_timezone
from zope.schema.interfaces import IContextAwareDefaultFactory
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from zope.interface import provider
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives
from plone.app.textfield import RichText
from z3c.form.browser.checkbox import SingleCheckBoxFieldWidget
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


grok.templatedir("templates")


def vocabulary_maker(l):
    vocab_list = []
    for row in l:
        entry = SimpleTerm(value=unicodedata.normalize('NFKD', row).encode('ascii', errors='ignore').decode('ascii'), title=_(row))
        vocab_list.append(entry)
    return SimpleVocabulary(vocab_list)


countries = vocabulary_maker([country.name for country in pycountry.countries])


class StartBeforeEnd(Invalid):
    __doc__ = _("error_invalid_date",
                default=u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def default_start(context):
    """Provide default start for the form.
    """
    return default_start_dt(context)


@provider(IContextAwareDefaultFactory)
def default_end(context):
    """Provide default end for the form.
    """
    return default_end_dt(context)


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
        description=_(u"Indicates the project title"),
        required=False,
    )

    description = schema.Text(
        title=_(u'label_description', default=u'Summary'),
        description=_(
            u'help_description',
            default=u'Used in item listings and search results.'
        ),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'project_image', default=u'Project Image'),
        description=u'',
        required=False,
    )

    start = schema.Datetime(
        title=_(
            u'label_event_start',
            default=u'Event Starts'
        ),
        description=_(
            u'help_event_start',
            default=u'Date and Time, when the event begins.'
        ),
        required=True,
        defaultFactory=default_start
    )
    directives.widget(
        'start',
        DatetimeFieldWidget,
        default_timezone=default_timezone,
        klass=u'event_start'
    )

    end = schema.Datetime(
        title=_(
            u'label_event_end',
            default=u'Event Ends'
        ),
        description=_(
            u'help_event_end',
            default=u'Date and Time, when the event ends.'
        ),
        required=True,
        defaultFactory=default_end
    )
    directives.widget(
        'end',
        DatetimeFieldWidget,
        default_timezone=default_timezone,
        klass=u'event_end'
    )

    whole_day = schema.Bool(
        title=_(
            u'label_event_whole_day',
            default=u'Whole Day'
        ),
        description=_(
            u'help_event_whole_day',
            default=u'Event lasts whole day.'
        ),
        required=False,
        default=False
    )
    directives.widget(
        'whole_day',
        SingleCheckBoxFieldWidget,
        klass=u'event_whole_day'
    )

    geolocation = schema.Choice(
        title=_(u"Geolocation"),
        description=_(u"Select country"),
        vocabulary=countries,
        required=True,
    )

    partners = RichText(
        title=_(u"Partners"),
        description=_(u""),
        required=False,
    )

    project_manager = schema.TextLine(
        title=_(u"Project Manager"),
        description=_(u""),
        required=False,
    )

    area = schema.List(
        title=_(u"Interest Areas"),
        description=_(u""),
        value_type=schema.Choice(
            source=ImprovementAreaList,
        ),
        required=False,
    )

    it_members = schema.TextLine(
        title=_(u"Improvement track team and members"),
        description=_(u""),
        required=False,
    )

    budget = schema.TextLine(
        title=_(u"Budget"),
        description=_(u""),
        required=False,
    )

    contribution = RichText(
        title=_(u"Contribution by partners and donors"),
        description=_(u""),
        required=False,
    )

    wop_program = schema.TextLine(
        title=_(u"WOP Program"),
        description=_(u""),
        required=False,
    )

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(
                _("error_end_must_be_after_start_date",
                  default=u"End date must be after start date.")
            )


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
