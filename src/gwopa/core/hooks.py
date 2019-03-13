from five import grok
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from gwopa.core.content.project import IProject
from gwopa.core.content.partner import IPartner
from gwopa.core.content.improvement_area import IImprovementArea
from gwopa.core.content.outcomecc import IOutcomecc
from gwopa.core.content.outcomeccs import IOutcomeccs
from plone import api
# import datetime
# import transaction


@grok.subscribe(IProject, IObjectAddedEvent)
def projectAdded(content, event):
    """ Project created handler to assign geolocation.
        Copy value from behaviour fields to project fields.projectAnd create
        current year workplan
    """

    api.content.create(
        type='Folder',
        id='files',
        title='Files',
        container=content)

    api.content.create(
        type='Folder',
        id='contribs',
        title='Contributors',
        container=content)

    areas = content.areas
    if areas:
        for area in areas:
            api.content.create(
                type='ImprovementArea',
                title=area,
                container=content)

    partners = content.partners
    if partners:
        for partner in partners:
            obj = api.content.create(
                type='ContribPartner',
                title=partner,
                container=content.contribs)
            obj.incash = 0
            obj.inkind = 0


@grok.subscribe(IProject, IObjectModifiedEvent)
def projectModified(content, event):
    """ Project modified handler.
        Create new areas
    """
    # zope.lifecycleevent.ObjectModifiedEvent
    print "project modified.... " + str(event)

    # new_areas = content.areas
    # current = [a.Title for a in api.content.find(portal_type="ImprovementArea", context=content, depth=1)]

    # new_areas = content.areas
    # if new_areas is None:
    #     return
    # else:
    #     for area in new_areas:
    #         if area not in current:
    #             api.content.create(
    #                 type='ImprovementArea',
    #                 title=area,
    #                 container=content)


@grok.subscribe(IPartner, IObjectAddedEvent)
@grok.subscribe(IPartner, IObjectModifiedEvent)
def partnerModified(content, event):
    """ Copy value from behaviour fields to project fields
    """
    # if content.geolocation:
    #     content.latitude = content.geolocation.latitude
    #     content.longitude = content.geolocation.longitude


@grok.subscribe(IImprovementArea, IObjectAddedEvent)
def improvementAreaAdded(content, event):
    """ Project created handler to assign geolocation.
        Copy value from behaviour fields to project fields.projectAnd create
        current year workplan
    """
    api.content.create(
        type='Folder',
        id='events',
        title='Events',
        container=content)

    api.content.create(
        type='Folder',
        id='files',
        title='Files',
        container=content)

    api.content.create(
        type='Folder',
        id='topics',
        title='Topics',
        container=content)

    api.content.create(
        type='OutcomeCC',
        id='outcomecc',
        title='OutcomeCC',
        container=content)


@grok.subscribe(IOutcomecc, IObjectAddedEvent)
@grok.subscribe(IOutcomeccs, IObjectAddedEvent)
def OutcomeCCAdded(content, event):
    """ Create the 13 CC vaues inside OutcomeCC or OutcomeCCS """
    items = api.content.find(portal_type="OutcomeCCItem")
    for item in items:
        api.content.create(
            type='OutcomeCCValues',
            id=item.id,
            title=item.Title,
            container=content)
