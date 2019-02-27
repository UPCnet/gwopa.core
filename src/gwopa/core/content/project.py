# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from plone.app.textfield import RichText
from zope.interface import Invalid
from zope.interface import invariant
from plone.namedfile import field as namedfile
from gwopa.core import _
from gwopa.core import utils
import datetime
from plone.directives import form
from plone import api
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from collective.geolocationbehavior.geolocation import IGeolocatable
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.autoform.interfaces import OMITTED_KEY
from zope.interface import Interface
# from plone.supermodel.directives import fieldset
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
import unicodedata
from zope.interface import directlyProvides


grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def default_today(context):
    """ Provide default start for the form. """
    return datetime.date.today()


@provider(IContextAwareDefaultFactory)
def default_tomorrow(context):
    """ Provide default end for the form. """
    return datetime.date.today() + datetime.timedelta(1)


ICategorization.setTaggedValue(OMITTED_KEY, [(Interface, 'language', 'true')])


def area_not_used(context):
    """ Titles of Improvement Areas not created in this Project """
    terms = []
    literals = api.content.find(portal_type="ItemArea", context=api.portal.get()['config']['areas'], depth=1)
    current_areas = api.content.find(portal_type="ImprovementArea", context=context, depth=1)
    areas = []
    for obj in current_areas:
        areas.append(obj.Title)
    for item in literals:
        if item.Title not in areas:
            flattened = unicodedata.normalize('NFKD', item.Title.decode('utf-8')).encode('ascii', errors='ignore')
            if item.Description:
                terms.append(SimpleVocabulary.createTerm(item.Title, flattened, item.Title + ' - (' + item.Description + ')'))
            else:
                terms.append(SimpleVocabulary.createTerm(item.Title, flattened, item.Title))
    return SimpleVocabulary(terms)


directlyProvides(area_not_used, IContextSourceBinder)


class IProject(model.Schema):
    """  Project type
    """

    # fieldset('project',
    #          label=_(u'Project'),
    #          fields=['title', 'image', 'objectives', 'start', 'end', 'wop_platform', 'country', 'wop_program']
    #          )

    # fieldset('members',
    #          label=_(u'Members'),
    #          fields=['partners', 'project_manager_admin', 'project_manager', 'members', 'budget', 'currency', 'contribution']
    #          )

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"Project title"),
        required=True,
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Image'),
        description=_(u'Project image'),
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

    objectives = RichText(
        title=_(u'Project description and main objectives'),
        required=False,
    )

    wop_platform = schema.Choice(
        title=_(u'Regional WOP Platform'),
        description=_(u"Platform/platforms associated to this project"),
        required=False,
        source=utils.listWOPPlatforms
    )

    wop_program = schema.Choice(
        title=_(u'WOP Program'),
        description=_(u"Program/programs associated to this project"),
        required=False,
        source=utils.listWOPPrograms
    )

    directives.widget('country', SelectWidget)
    country = schema.Choice(
        title=_(u"Country"),
        description=_(u"Select country"),
        source=utils.countries,
        required=True,
    )

    # form.mode(latitude='hidden')
    latitude = schema.Float(
        title=_(u"Latitude"),
        required=False,
        default=0.0
    )

    # form.mode(longitude='hidden')
    longitude = schema.Float(
        title=_(u"Longitude"),
        required=False,
        default=0.0
    )

    directives.widget('partners', SelectWidget)
    partners = schema.List(
        title=_(u"Partners"),
        description=_(u"Partner/partners of the project"),
        required=False,
        value_type=schema.Choice(
            source=utils.listPartners,
        ),
    )

    project_manager_admin = schema.Choice(
        title=_(u"Project Manager Admin"),
        description=_(u"The responsible manager of the project"),
        required=False,
        vocabulary=u'plone.app.vocabularies.Users',
    )

    directives.widget('project_manager', SelectWidget)
    project_manager = schema.Choice(
        title=_(u"Project Manager"),
        description=_(u"The responsible of this project"),
        required=False,
        vocabulary=u'plone.app.vocabularies.Users',
    )

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Members"),
        description=_(u"Improvement track team and members"),
        required=False,
        value_type=schema.Choice(
            source='plone.app.vocabularies.Users',
        )
    )

    budget = schema.Int(
        title=_(u"Total budget"),
        required=False,
    )

    currency = schema.Choice(
        title=_(u"Currency"),
        source=utils.settings_currency,
        required=True,
    )

    contribution = RichText(
        title=_(u"Contribution by partners and donors"),
        description=_(u""),
        required=False,
    )

    directives.widget('areas', SelectWidget)
    areas = schema.List(
        title=_(u"Working Areas"),
        description=_(u"Select one or more associated Working Area"),
        required=False,
        value_type=schema.Choice(
            source=area_not_used,
        )
    )

    form.mode(gwopa_code_project='hidden')
    # form.mode(IEditForm, gwopa_code_project='display')
    gwopa_code_project = schema.ASCIILine(
        title=_(u'CODE'),
        description=_(u'Internal CODE for administrators'),
        required=False
    )


@form.default_value(field=IProject['gwopa_code_project'])
def codeDefaultValue(data):
    # TODO: Sort ids to assign the next one, to bypass
    # empty/missing values on delete
    items = len(api.content.find(
        portal_type='Project',
        context=data.context))

    return 'PR-{0}'.format(str(items + 1).zfill(3))

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(u"End date must be after start date.")


class View(grok.View):
    grok.context(IProject)
    grok.template('project_view')

    def getImprovementAreas(self):
        items = api.content.find(
            portal_type='ImprovementArea',
            path='/'.join(self.context.getPhysicalPath()),
            depth=1)
        results = []
        for item in items:
            obj = item.getObject()
            if obj.image is None:
                image = obj.absolute_url_path() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
            else:
                image = obj.absolute_url_path() + '/@@images/image/thumb'
            results.append(dict(
                title=item.Title,
                image=image,
                url='/'.join(obj.getPhysicalPath()),
                description=item.description))
        return results

    def get_currency(self):
        value = getattr(self.context, 'currency', None)
        if value == 'Dollars':
            return "$"
        elif value == 'Pounds':
            return "£"
        elif value == 'Euros':
            return "€"
        else:
            return value

    def google_maps_link(self):
        geo = IGeolocatable(self.context, None)
        if geo:
            coordinates = [geo.geolocation.latitude, geo.geolocation.longitude]
            if geo.geolocation.latitude != 0.0 and geo.geolocation.longitude != 0.0:
                maps_link = "//www.google.com/maps/place/{0}+{1}/@{0},{1},17z".format(  # noqa
                    coordinates[0],
                    coordinates[1]
                )
                return maps_link

        return None
