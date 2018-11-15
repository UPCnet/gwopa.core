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


grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


@provider(IContextAwareDefaultFactory)
def default_today(context):
    """Provide default start for the form. """
    return datetime.date.today()


@provider(IContextAwareDefaultFactory)
def default_tomorrow(context):
    """Provide default end for the form. """
    return datetime.date.today() + datetime.timedelta(1)


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

    country = schema.Choice(
        title=_(u"Country"),
        description=_(u"Select country"),
        vocabulary=utils.countries,
        required=True,
    )

    form.mode(latitude='hidden')
    latitude = schema.Float(
        title=_(u"Latitude"),
        required=False,
        default=0.0
    )

    form.mode(longitude='hidden')
    longitude = schema.Float(
        title=_(u"Longitude"),
        required=False,
        default=0.0
    )

    partners = schema.List(
        title=_(u"Partners"),
        description=_(u"Partner/partners associated to this project"),
        required=False,
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.partners_list'),
        ),
    )

    project_manager_admin = schema.Choice(
        title=_(u"Project Manager Admin"),
        description=_(u"The responsible of this project"),
        required=False,
        vocabulary=u'plone.app.vocabularies.Users',
    )

    project_manager = schema.Choice(
        title=_(u"Project Manager"),
        description=_(u"The responsible of this project"),
        required=False,
        vocabulary=u'plone.app.vocabularies.Users',
    )

    # area = schema.List(
    #     title=_(u"Interest Areas"),
    #     description=_(u""),
    #     value_type=schema.Choice(
    #         source=ImprovementAreaList,
    #     ),
    #     required=False,
    # )

    members = schema.List(
        title=_(u"Members"),
        description=_(u"Improvement track team and members"),
        required=False,
        value_type=schema.Choice(
            source='plone.app.vocabularies.Users',
        )
    )

    budget = schema.Int(
        title=_(u"Budget"),
        required=False,
    )

    currency = schema.Choice(
        title=_(u"Currency"),
        source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.currency'),
        required=True,
    )

    contribution = RichText(
        title=_(u"Contribution by partners and donors"),
        description=_(u""),
        required=False,
    )

    wop_program = schema.List(
        title=_(u"WOP Program"),
        description=_(u"Program/programs associated to this project"),
        value_type=schema.Choice(
            source=utils.vocabulary_values('gwopa.core.controlpanel.IGWOPASettings.wop_list'),
        ),
        required=False,
    )

    risks = RichText(
        title=_(u'Risks'),
        required=False,
    )

    assumptions = RichText(
        title=_(u'Assumptions'),
        required=False,
    )

    objectives = RichText(
        title=_(u'Objectives'),
        required=False,
    )

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(u"End date must be after start date.")


class View(grok.View):
    grok.context(IProject)
    grok.template('project_view')

    def getImprovementAreas(self):
        items = api.content.find(portal_type='ImprovementArea')
        results = []
        for item in items:
            obj = item.getObject()
            if obj.image is None:
                image = obj.absolute_url_path() + '/++theme++gwopa.theme/assets/images/200x200.png'
            else:
                image = obj.absolute_url_path() + '/@@images/image/thumb'
            results.append(dict(
                title=item.Title,
                image=image,
                url=item.getPath(),
                description=item.description))
        return results
