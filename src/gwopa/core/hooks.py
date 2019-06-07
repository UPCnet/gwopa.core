from five import grok
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from gwopa.core.content.project import IProject
from gwopa.core.content.partner import IPartner
from gwopa.core.content.improvement_area import IImprovementArea
from gwopa.core.content.outcomecc import IOutcomecc
from gwopa.core.content.outcomeccs import IOutcomeccs
from Products.CMFPlone.interfaces import IConfigurationChangedEvent
from Products.PluggableAuthService.interfaces.events import IUserLoggedInEvent
from plone import api
import requests
from plone.namedfile.file import NamedBlobImage
# import datetime
import transaction
import math
from dateutil.relativedelta import *
from zope.globalrequest import getRequest
import dateutil.relativedelta
from zope.annotation.interfaces import IAnnotations


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
    content.gwopa_year_phases = int(math.ceil(float((content.completionactual - content.startactual).days) / float(365)))

    # Asign default image if not set
    if content.image is None:
        data = requests.get(api.portal.get().aq_parent.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg', verify=False, timeout=10).content
        default_image = NamedBlobImage(data=data,
                                       filename=u'image.jpg',
                                       contentType='image/jpeg')
        content.image = default_image

    # Assign values to fases
    fases = int(math.ceil(float((content.completionactual - content.startactual).days) / float(365)))
    date1 = content.startactual
    date2 = content.completionactual
    datas = [(date1 + relativedelta(years=i)).strftime("%B %d, %Y") for i in range(date2.year - date1.year + 1)] + [date2.strftime("%B %d, %Y")]
    isodate = [(date1 + relativedelta(years=i)).strftime("%Y-%m-%d") for i in range(date2.year - date1.year + 1)] + [date2.strftime("%Y-%m-%d")]
    patterndate = [(date1 - dateutil.relativedelta.relativedelta(months=1) + relativedelta(years=i)).strftime("%Y %m %d").replace(' 0', ' ').replace(' ', ',') for i in range(date2.year - date1.year + 1)]
    patterndate.append((date2 - dateutil.relativedelta.relativedelta(months=1)).strftime("%Y %m %d").replace(' 0', ' ').replace(' ', ','))

    results = []
    if fases > 1:
        count = 0
        while count != fases:
            results.append(dict(
                start=datas[0 + count],
                end=datas[1 + count],
                start_iso=isodate[0 + count],
                end_iso=isodate[1 + count],
                pattern_start=patterndate[0 + count],
                pattern_end=patterndate[1 + count],
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
            pattern_start=patterndate[0],
            pattern_end=patterndate[1],
            fase=1
        ))
    content.gwopa_year_phases = results

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

        # Asign default image if not set
        if content.image is None:
            data = requests.get(api.portal.get().aq_parent.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg', verify=False, timeout=10).content
            default_image = NamedBlobImage(data=data,
                                           filename=u'image.jpg',
                                           contentType='image/jpeg')
            content.image = default_image

        # Assign values to fases
        fases = int(math.ceil(float((content.completionactual - content.startactual).days) / float(365)))
        date1 = content.startactual
        date2 = content.completionactual
        datas = [(date1 + relativedelta(years=i)).strftime("%B %d, %Y") for i in range(date2.year - date1.year + 1)] + [date2.strftime("%B %d, %Y")]
        isodate = [(date1 + relativedelta(years=i)).strftime("%Y-%m-%d") for i in range(date2.year - date1.year + 1)] + [date2.strftime("%Y-%m-%d")]
        patterndate = [(date1 - dateutil.relativedelta.relativedelta(months=1) + relativedelta(years=i)).strftime("%Y %m %d").replace(' 0', ' ').replace(' ', ',') for i in range(date2.year - date1.year + 1)]
        patterndate.append((date2 - dateutil.relativedelta.relativedelta(months=1)).strftime("%Y %m %d").replace(' 0', ' ').replace(' ', ','))

        results = []
        if fases > 1:
            count = 0
            while count != fases:
                results.append(dict(
                    start=datas[0 + count],
                    end=datas[1 + count],
                    start_iso=isodate[0 + count],
                    end_iso=isodate[1 + count],
                    pattern_start=patterndate[0 + count],
                    pattern_end=patterndate[1 + count],
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
                pattern_start=patterndate[0],
                pattern_end=patterndate[1],
                fase=1
            ))
        content.gwopa_year_phases = results

        # Assign Areas
        new_areas = content.areas
        current = [a.Title for a in api.content.find(portal_type="ImprovementArea", context=content, depth=1)]

        new_areas = content.areas
        if new_areas is None:
            return
        else:
            for area in new_areas:
                if area not in current:
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

    obj = api.content.create(
            type='OutcomeCC',
            id='outcomecc',
            title='OutcomeCC',
            container=content)

    annotations = IAnnotations(obj)
    for x in range(0, 11):  # Create 10 annotations
        generic = []
        outcomeccgeneric_info = dict(
            id_specific = obj.id,
            description = obj.description,
            baseline=obj.baseline,
            baseline_date=obj.baseline_date,
            objective=obj.objective,
            objective_date=obj.objective_date,
            stage='',
        )
        generic.append(outcomeccgeneric_info)
        specifics = []
        monitoring = []
        items = api.content.find(
            portal_type=['OutcomeCCS'],
            context=content)
        for item in items:
            specific_obj = item.getObject()
            result = api.content.find(portal_type="OutcomeCCItem", Title=specific_obj.title)[0]
            capacitychanges_obj = result.getObject()
            category = capacitychanges_obj.short_category
            outcomeccspecific_info = dict(
                id_specific = specific_obj.id,
                title_specific = specific_obj.title,
                description = specific_obj.description,
                url='/'.join(specific_obj.getPhysicalPath()),
                selected_specific='',
                icon_url='++theme++gwopa.theme/assets/images/' + capacitychanges_obj.id + '.png',
                icon_url_selected='++theme++gwopa.theme/assets/images/w-' + capacitychanges_obj.id + '.png',
                short_category=category,
                baseline=specific_obj.baseline,
                baseline_date=specific_obj.baseline_date,
                objective=specific_obj.objective,
                objective_date=specific_obj.objective_date,
            )
            specifics.append(outcomeccspecific_info)
            outcomeccmonitoring_info = dict(
                id_specific = specific_obj.id,
                title_specific = specific_obj.title,
                description = specific_obj.description,
                url='/'.join(specific_obj.getPhysicalPath()),
                selected_specific='',
                icon_url='++theme++gwopa.theme/assets/images/' + capacitychanges_obj.id + '.png',
                icon_url_selected='++theme++gwopa.theme/assets/images/w-' + capacitychanges_obj.id + '.png',
                icon_basic='++theme++gwopa.theme/assets/images/g-' + capacitychanges_obj.id + '.png',
                short_category=category,
                baseline=specific_obj.baseline,
                baseline_date=specific_obj.baseline_date,
                objective=specific_obj.objective,
                objective_date=specific_obj.objective_date,
                degree_changes='',
                contributed_project='',
                contributing_factors='',
                obstacles='',
                limiting_factors='',
                consensus='',
                explain='',
                selected_monitoring='empty',
            )
            monitoring.append(outcomeccmonitoring_info)

        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
        annotations[KEY] = data

@grok.subscribe(IOutcomecc, IObjectAddedEvent)
# @grok.subscribe(IOutcomeccs, IObjectAddedEvent)
def OutcomeCCAdded(content, event):
    """ Create the 13 CC vaues inside OutcomeCC or OutcomeCCS """
    items = api.content.find(portal_type="OutcomeCCItem")
    for item in items:
        api.content.create(
            type='OutcomeCCS',
            id=item.id,
            title=item.Title,
            container=content)
        transaction.commit()


@grok.subscribe(IConfigurationChangedEvent)
def updateCustomLangCookie(event):
    """ This subscriber will trigger when a user change his/her profile data. It
        sets a cookie for the 'language' user profile setting. After this, due
        to the custom Language Negotiator  the site language is forced to
        the one in the cookie.
    """
    if 'language' in event.data:
        if event.data['language']:
            event.context.request.response.setCookie('I18N_LANGUAGE', event.data['language'], path='/')
            event.context.request.response.redirect(event.context.context.absolute_url() + '/@@personal-information')


@grok.subscribe(IUserLoggedInEvent)
def updateCustomLangCookieLogginIn(event):
    """ This subscriber will trigger when a user change his/her profile data. It
        sets a cookie for the 'language' user profile setting. After this, due
        to the custom Language Negotiator the site language is forced to
        the one in the cookie.
    """
    request = getRequest()
    current = api.user.get_current()
    lang = current.getProperty('language')
    if lang and request is not None:
        request.response.setCookie('I18N_LANGUAGE', lang, path='/')
