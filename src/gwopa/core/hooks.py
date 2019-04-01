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
import transaction
import math
from dateutil.relativedelta import *


@grok.subscribe(IProject, IObjectAddedEvent)
def projectAdded(content, event):
    """ Project created handler to assign geolocation.
        Copy value from behaviour fields to project fields.projectAnd create
        current year
    """

    # Grant Editor/Reader role to members in project
    if content.members:
        for user in content.members:
            api.user.grant_roles(username=user, obj=content, roles=['Editor', 'Reader'])

    # Assign fases to internal field
    content.gwopa_fases = int(math.ceil(float((content.completionactual - content.startactual).days) / float(365)))

    # Create default needed folders in the new project
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

    # Create Working Areas
    areas = content.areas
    if areas:
        for area in areas:
            data = api.content.find(portal_type="ItemArea", Title=area)[0]
            obj = api.content.create(
                type='ImprovementArea',
                title=data.Title,
                description=data.Description,
                image=data.getObject().image,
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
        Create new areas.newSometimes this code is executed and the project is not edited.
        In example, changing permissions, this hook is executed.
        We check the transition when edit, and seems to be:
             zope.lifecycleevent.ObjectModifiedEvent

    """
    # Really check if project is modified
    if 'zope.lifecycleevent.ObjectModifiedEvent' in str(event):

        # Grant Editor/Reader role to members in project
        if content.members:
            for user in content.members:
                api.user.grant_roles(username=user, obj=content, roles=['Editor', 'Reader'])

        # Assign values to fases
        fases = int(math.ceil(float((content.completionactual - content.startactual).days) / float(365)))
        date1 = content.startactual
        date2 = content.completionactual
        datas = [(date1 + relativedelta(years=i)).strftime("%B %d, %Y") for i in range(date2.year - date1.year + 1)]
        datas.append(content.completionactual.strftime("%B %d, %Y"))
        isodate = [(date1 + relativedelta(years=i)).strftime("%Y-%d-%m") for i in range(date2.year - date1.year + 1)]
        isodate.append(content.completionactual.strftime("%Y-%d-%m"))

        results = []
        if fases > 1:
            count = 0
            while count != fases:
                results.append(dict(
                    start=datas[0 + count],
                    end=datas[1 + count],
                    start_iso=isodate[0 + count],
                    end_iso=isodate[1 + count],
                    fase=count + 1
                ))
                count = count + 1
        else:
            count = 0
            results.append(dict(
                start=datas[0],
                end=datas[1],
                start_iso=isodate[0],
                end_iso=isodate[1],
                fase=1
            ))
        content.gwopa_fases = results

        new_areas = content.areas
        current = [a.Title for a in api.content.find(portal_type="ImprovementArea", context=content, depth=1)]

        new_areas = content.areas
        if new_areas is None:
            return
        else:
            for area in new_areas:
                if area not in current:
                    print "Created Improvement Area: " + area
                    data = api.content.find(portal_type="ItemArea", Title=area)[0]
                    api.content.create(
                        type='ImprovementArea',
                        title=data.Title,
                        description=data.Description,
                        image=data.getObject().image,
                        container=content)


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
        current year
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
        transaction.commit()
