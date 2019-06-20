# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from zope.schema.interfaces import IContextAwareDefaultFactory
from zope.interface import provider
from plone.app.textfield import RichText
from zope.interface import Invalid
from plone.namedfile import field as namedfile
from gwopa.core import _
from gwopa.core import utils
import datetime
from plone import api
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.autoform.interfaces import OMITTED_KEY
from zope.interface import Interface
from plone.supermodel.directives import fieldset
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from plone.app.z3cform.widget import AjaxSelectFieldWidget
import unicodedata
from zope.interface import directlyProvides
# from zope.schema.vocabulary import SimpleTerm
from operator import itemgetter
from plone.directives import form
from collective import dexteritytextindexer
from Products.CMFCore.utils import getToolByName


ICategorization.setTaggedValue(OMITTED_KEY, [(Interface, 'language', 'true')])

grok.templatedir("templates")


def theDefaultValue():
    return datetime.date.today() - datetime.timedelta(1)


def maxValue():
    return datetime.date(2015, 5, 12)


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def default_today(context):
    """ Provide default start for the form. """
    return datetime.date.today()


@provider(IContextAwareDefaultFactory)
def default_plus_one_year(context):
    """ Provide default end for the form. """
    return datetime.date.today() + datetime.timedelta(365)


def area_not_used(context):
    """ Titles of Improvement Areas not created in this Project """
    terms = []
    literals = api.content.find(portal_type="ItemArea", context=api.portal.get()['config']['areas'], depth=1)
    for item in literals:
        flattened = unicodedata.normalize('NFKD', item.Title.decode('utf-8')).encode('ascii', errors='ignore')
        terms.append(SimpleVocabulary.createTerm(item.Title, flattened, item.Title))
    return SimpleVocabulary(terms)


directlyProvides(area_not_used, IContextSourceBinder)


class IProject(model.Schema):
    """  Project type
    """

    fieldset('project',
             label=_(u'Project'),
             fields=['title', 'objectives', 'areas', 'wop_platform', 'wop_program', 'currency', 'total_budget', 'measuring_frequency', 'category']
             )

    fieldset('image',
             label=_(u'Image'),
             fields=['image']
             )

    fieldset('dates',
             label=_(u'Dates'),
             fields=['startdate', 'startactual', 'startplanned', 'completiondate', 'completionactual', 'completionplanned', 'gwopa_year_phases']
             )

    fieldset('geo',
             label=_(u'Geolocation'),
             fields=['country', 'location', 'latitude', 'longitude']
             )

    fieldset('members',
             label=_(u'Partners'),
             fields=['partners', 'project_manager_admin', 'project_manager', 'members']
             )

    dexteritytextindexer.searchable('category')
    category = schema.Tuple(
        title=_(u'label_tags', default=u'Tags'),
        description=_(
            u'help_tags',
            default=u'Tags are commonly used for ad-hoc organization of content.'
        ),
        value_type=schema.TextLine(),
        required=False,
        missing_value=(),
    )
    directives.widget(
        'category',
        AjaxSelectFieldWidget,
        vocabulary='plone.app.vocabularies.Keywords'
    )

    dexteritytextindexer.searchable('title')
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

    measuring_frequency = schema.Choice(
        title=_(u"Measuring frequency"),
        description=_(u"Frequency used for all the items of the project."),
        source=utils.settings_measuring_frequency,
        required=True,
    )

    directives.mode(startdate='display')
    startdate = schema.Text(
        title=_(u"Starting date"),
        description=_(u"The dates when the project has started. Planned date and current date.")
    )

    startactual = schema.Date(
        title=_(u'Actual'),
        required=True,
        defaultFactory=default_today
    )

    startplanned = schema.Date(
        title=_(u'Planned'),
        required=False,
    )

    directives.mode(completiondate='display')
    completiondate = schema.Text(
        title=_(u"Completion date"),
        description=_(u"The dates when the project has been completed. Planned date and current date.")
    )

    completionactual = schema.Date(
        title=_(u'Actual'),
        required=True,
        defaultFactory=default_plus_one_year
    )

    completionplanned = schema.Date(
        title=_(u'Planned'),
        required=False,
    )

    dexteritytextindexer.searchable('objectives')
    objectives = RichText(
        title=_(u'Project description and main objectives'),
        description=_(u'Use this area to add all the objectives and description of the project'),
        required=False,
    )

    dexteritytextindexer.searchable('wop_platform')
    wop_platform = schema.Choice(
        title=_(u'Regional WOP Platform'),
        description=_(u"Platform/platforms associated to this project"),
        required=False,
        source=utils.listWOPPlatforms
    )

    dexteritytextindexer.searchable('wop_program')
    wop_program = schema.Choice(
        title=_(u'WOP Program'),
        description=_(u"Program/programs associated to this project"),
        required=False,
        source=utils.listWOPPrograms
    )

    # directives.widget('country', SelectWidget)
    dexteritytextindexer.searchable('country')
    country = schema.Choice(
        title=_(u"Country"),
        description=_(u"Select a country from the list"),
        source=utils.countries,
        required=True,
    )

    dexteritytextindexer.searchable('location')
    location = schema.TextLine(
        title=_(u"Location"),
        description=_(u"Write the project location"),
        required=False,
    )

    latitude = schema.TextLine(
        title=_(u"Latitude"),
        description=_(u"Latitude of this project. Used in the map view"),
        required=False,
    )

    longitude = schema.TextLine(
        title=_(u"Longitude"),
        description=_(u"Longitude of this project. Used in the map view"),
        required=False,
    )

    dexteritytextindexer.searchable('partners')
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
    project_manager = schema.List(
        title=_(u"Project Manager"),
        description=_(u"The responsible of this project"),
        required=False,
        value_type=schema.Choice(
            source='plone.app.vocabularies.Users',
        )
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

    currency = schema.Choice(
        title=_(u"Currency"),
        description=_(u"The currency used into the project"),
        source=utils.settings_currency,
        required=True,
    )

    # directives.widget('areas', SelectWidget)
    areas = schema.List(
        title=_(u"Working Areas"),
        description=_(u"Select one or more associated Working Area"),
        required=False,
        value_type=schema.Choice(
            source=area_not_used,
        )
    )

    form.mode(gwopa_year_phases='hidden')
    gwopa_year_phases = schema.ASCIILine(
        title=_(u'Fases'),
        required=False
    )

    form.mode(total_budget='hidden')
    total_budget = schema.ASCIILine(
        title=_(u'Total budget'),
        required=False,
        readonly=True
    )


class View(grok.View):
    grok.context(IProject)
    grok.template('project_view')
    grok.require('zope2.View')

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
                description=item.Description))
        results.sort(key=lambda x: x['title'], reverse=False)
        return results

    def startplanneddates(self):
        if not self.context.startplanned or self.context.startplanned == '' or (self.context.startplanned == self.context.startactual):
            return False
        else:
            return True

    def completionplanneddates(self):
        if not self.context.completionplanned or self.context.completionplanned == '' or (self.context.completionactual == self.context.completionplanned):
            return False
        else:
            return True

    def getProject_manager(self):
        users = []
        results = []
        if self.context.project_manager_admin:
            users.append(self.context.project_manager_admin)
        if self.context.project_manager:
            for user in self.context.project_manager:
                users.append(user)

        uniqueUsers = [u for u in set(users)]  # Returns unique values in list

        for user in uniqueUsers:
            obj = api.user.get(username=user)
            manager = False
            project = False
            if self.context.project_manager_admin:
                if user in self.context.project_manager_admin:
                    manager = 'admin-partner'
            if self.context.project_manager:
                if user in self.context.project_manager:
                    project = True
            results.append(dict(
                partners=obj.getProperty('wop_partners'),
                name=obj.getProperty('fullname'),
                id=obj.getProperty('id'),
                email=obj.getProperty('email'),
                image=utils.getPortrait(self, user),
                managerClass=manager,
                project=project,
            ))
        return sorted(results, key=itemgetter('name'), reverse=False)

    def canEdit(self):
        # TODO: Create app role system
        currentuser = api.user.get_current().id
        roles = ['Manager', 'Contributor', 'Editor']
        for role in roles:
            if role in api.user.get_roles(username=currentuser):
                return True
        return False

    def getPath(self):
        return '/'.join(self.context.getPhysicalPath())

    def getPartners(self):
        other = api.content.find(
            portal_type=['ContribPartner'],
            path='/'.join(self.context.getPhysicalPath()) + '/contribs/',
            depth=2)
        results = []
        letter = utils.project_currency(self)
        for item in other:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                edit=item.getURL() + '/edit',
                incash=str(0 if obj.incash is None else obj.incash) + ' ' + str(letter),
                inkind=str(0 if obj.inkind is None else obj.inkind) + ' ' + str(letter),
            ))
        return results

    def getMembers(self):
        """ Returns Site Members """
        users = self.context.members
        results = []
        if users is None:
            return []
        else:
            for user in users:
                obj = api.user.get(username=user)
                results.append(dict(
                    name=obj.getProperty('fullname'),
                    id=obj.getProperty('id'),
                    email=obj.getProperty('email'),
                    image=utils.getPortrait(self, user),
                ))
            return sorted(results, key=itemgetter('name'), reverse=False)

    def getFiles(self):
        """ Return files of the Area """
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['File'],
            path={'query': '/'.join(self.context.getPhysicalPath()) + '/files',
                  'depth': 1},
            sort_on=('effective'),
            sort_order='reverse',
            sort_limit=5)
        results = []
        if len(items) != 0:
            lang = api.portal.get_current_language()
            if lang == 'es':
                FORMAT_DATE = '%d/%m/%Y'
            else:
                FORMAT_DATE = '%m/%d/%Y'
            for item in items:
                results += [{'title': item.Title,
                             'portal_type': item.portal_type,
                             'url': item.getURL(),
                             'date': item.modification_date.strftime(FORMAT_DATE)
                             }]
            return results
        else:
            return None

    def donors(self):
        other = api.content.find(
            portal_type=['ContribDonor'],
            path='/'.join(self.context.getPhysicalPath()) + '/contribs/',
            depth=2)
        results = []
        letter = utils.project_currency(self)
        for item in other:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                edit=item.getURL() + '/edit',
                incash=str(0 if obj.incash is None else obj.incash) + ' ' + str(letter),
                inkind=str(0 if obj.inkind is None else obj.inkind) + ' ' + str(letter),
            ))
        return results

    def others(self):
        other = api.content.find(
            portal_type=['ContribOther'],
            path='/'.join(self.context.getPhysicalPath()) + '/contribs/',
            depth=2)
        results = []
        letter = utils.project_currency(self)
        for item in other:
            obj = item.getObject()
            results.append(dict(
                title=item.Title,
                edit=item.getURL() + '/edit',
                incash=str(0 if obj.incash is None else obj.incash) + ' ' + str(letter),
                inkind=str(0 if obj.inkind is None else obj.inkind) + ' ' + str(letter),
            ))
        return results

    def get_budget(self):
        # Assign total_budget value to index. Needed to find by value in Project Global Map
        if self.context.total_budget == 0:
            return None
        else:
            letter = utils.project_currency(self)
            return str(self.context.total_budget) + ' ' + letter
