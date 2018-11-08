from five import grok
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from gwopa.core.content.project import IProject
# from gwopa.core.content.improvement_area import IImprovementArea


@grok.subscribe(IProject, IObjectAddedEvent)
def projectModified(content, event):
    """ Project created handler to assign geolocation.
        Copy value from behaviour fields to project fields
    """
    if content.geolocation:
        content.latitude = content.geolocation.latitude
        content.longitude = content.geolocation.longitude


# @grok.subscribe(IImprovementArea, IObjectAddedEvent)
# def areaModified(content, event):
#     """ Project created handler to assign geolocation.
#         Copy value from behaviour fields to project fields
#     """
#     import ipdb; ipdb.set_trace()
