# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from plone.app.event.base import default_timezone
from zope.schema.interfaces import IContextAwareDefaultFactory
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from zope.interface import provider
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.autoform import directives
from zope.interface import Invalid
from zope.interface import invariant
from gwopa.core import _

grok.templatedir("templates")


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


class IQualitativeindicator(model.Schema):
    """  Project type
    """
    title = schema.TextLine(
        title=_(u"Project name"),
        description=_(u"Indicates the project title"),
        required=False,
    )

    # description = schema.Text(
    #     title=_(u'label_description', default=u'Summary'),
    #     description=_(
    #         u'help_description',
    #         default=u'Used in item listings and search results.'
    #     ),
    #     required=False,
    #     missing_value=u'',
    # )

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

    @invariant
    def validate_start_end(data):
        if (data.start and data.end and data.start > data.end):
            raise StartBeforeEnd(
                _("error_end_must_be_after_start_date",
                  default=u"End date must be after start date.")
            )


class View(grok.View):
    grok.context(IQualitativeindicator)
    grok.template('qualitative_view')
