from five import grok
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from gwopa.core.content.project import IProject
from gwopa.core.content.partner import IPartner
# from gwopa.core.content.improvement_area import IImprovementArea
from plone import api
import datetime


@grok.subscribe(IProject, IObjectAddedEvent)
def projectAdded(content, event):
    """ Project created handler to assign geolocation.
        Copy value from behaviour fields to project fields.projectAnd create
        current year workplan
    """
    if content.geolocation:
        content.latitude = content.geolocation.latitude
        content.longitude = content.geolocation.longitude
    year = datetime.datetime.now().year
    api.content.create(
        type='WorkPlan',
        id='awp-' + str(year),
        container=content)


@grok.subscribe(IProject, IObjectModifiedEvent)
def projectModified(content, event):
    """ Project modified handler to assign geolocation.
        Copy value from behaviour fields to project fields
    """
    if content.geolocation:
        content.latitude = content.geolocation.latitude
        content.longitude = content.geolocation.longitude


@grok.subscribe(IPartner, IObjectAddedEvent)
@grok.subscribe(IPartner, IObjectModifiedEvent)
def partnerModified(content, event):
    """ Copy value from behaviour fields to project fields
    """
    if content.geolocation:
        content.latitude = content.geolocation.latitude
        content.longitude = content.geolocation.longitude
