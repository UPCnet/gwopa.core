# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from zope.schema.interfaces import IContextAwareDefaultFactory
from plone.app.event.base import default_end as default_end_dt
from plone.app.event.base import default_start as default_start_dt
from zope.interface import provider
from zope.interface import Invalid
from gwopa.core import _

grok.templatedir("templates")


class StartBeforeEnd(Invalid):
    __doc__ = _(u"Invalid start or end date")


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


class IOutcomeindicator(model.Schema):
    """  Outcome indicator
    """
    title = schema.TextLine(
        title=_(u"Outcome"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )


class View(grok.View):
    grok.context(IOutcomeindicator)
    grok.template('outcomeindicator_view')
