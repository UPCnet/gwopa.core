# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from decimal import Decimal
from geojson import Feature
from geojson import Point
from operator import itemgetter
from plone import api
from plone.protect.interfaces import IDisableCSRFProtection
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides

from gwopa.core import _
from gwopa.core.utils import getDictTranslatedContributingFromList
from gwopa.core.utils import getDictTranslatedObstaclesFromList
from gwopa.core.utils import getTitleAttrLang
from gwopa.core.utils import getTranslatedConsensusFromID
from gwopa.core.utils import getTranslatedContributedProjectFromID
from gwopa.core.utils import getTranslatedDegreeChangesFromID
from gwopa.core.utils import getUserLang

import datetime
import json


class getPhases(BrowserView):
    # /api-getphases
    def __call__(self):
        if self.context.portal_type == 'Project':
            project = self.context
        else:
            project = self.context.aq_parent
        results = []
        results = [{'phases': len(project.gwopa_year_phases),
                    'gwopa_year_phases': project.gwopa_year_phases,
                    }]
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getOutputs(BrowserView):
    # /api-getOutputs
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Outputdefaults')
        literals = sorted(literals, key=itemgetter('Title'), reverse=False)
        for item in literals:
            results.append(dict(
                name=item.Title))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getMainObstacles(BrowserView):
    # /api-getMainObstacles
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Mainobstacles')

        attr_lang = getTitleAttrLang()
        for item in literals:
            results.append({'id': item.Title,
                            'name': getattr(item.getObject(), attr_lang.lower())})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))


class getMainContributing(BrowserView):
    # /api-getMainContributing
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Maincontributing')

        attr_lang = getTitleAttrLang()
        for item in literals:
            results.append({'id': item.Title,
                            'name': getattr(item.getObject(), attr_lang.lower())})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))


class getOutcomes(BrowserView):
    # /api-getOutcomes
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Outcomedefaults')

        attr_lang = getTitleAttrLang()
        for item in literals:
            results.append({'id': item.Title,
                            'name': getattr(item.getObject(), attr_lang.lower())})
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))


class getUsers(BrowserView):

    def __call__(self):
        results = []
        if self.context.members is None:
            results.append(dict(id="-1", text="There aren't members assigned to this project"))
        else:
            for member in self.context.members:
                user = api.user.get(member)
                results.append(dict(
                    id=user.id,
                    text=user.getProperty('fullname')))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results, })


class getUnits(BrowserView):
    # /api-getUnits
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().measuring_unit_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang]})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))

class getRolesPartner(BrowserView):
    # /api-getRolesPartner
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().partner_roles_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang]})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))

class getRolesOtherContributor(BrowserView):
    # /api-getRolesPartner
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().organization_roles_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang]})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))

class getOverallScore(BrowserView):
    # /api-getRolesPartner
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().overall_score_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang]})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))

class getDegree(BrowserView):
    # /api-getDegree
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().degree_changes_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang],
                                'num': float(value.split(' ')[0])})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['num']))


class getContributed(BrowserView):
    # /api-getContributed
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().contributed_project_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang]})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))


class getConsensus(BrowserView):
    # /api-getConsensus
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        lang = getUserLang()
        item = api.content.find(portal_type="SettingsPage", id='settings')
        results = []
        if item:
            values = item[0].getObject().consensus_dict
            for value in values.keys():
                results.append({'id': value,
                                'name': values[value][lang]})

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(sorted(results, key=lambda k: k['name']))


class Delete(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        item = self.request.form.get('item')
        obj = api.content.get(path=item)
        api.content.delete(obj=obj, check_linkintegrity=False)
        return 'Ok, item deleted'


class CreatePartner(BrowserView):

    def __call__(self):
        item = api.content.find(path=self.request.form.get('item_path'), depth=0)[0]
        project = api.content.find(path=self.request.form.get('item_path').replace('/contribs', ''), depth=0)[0].getObject()
        title = self.request.form.get('item_title')
        portal_type = self.request.form.get('item_type')
        obj = api.content.create(
            title=title,
            type=portal_type,
            container=item.getObject())
        obj.organization_roles = self.request.form.get('item_roles')
        obj.incash = Decimal(self.request.form.get('item_incash').replace(',', ''))
        obj.inkind = Decimal(self.request.form.get('item_inkind').replace(',', ''))
        if project.total_budget is None:
            value = 0
        else:
            value = project.total_budget
        project.total_budget = value + obj.incash + obj.inkind
        return 'Ok, item created'


class addTitleOutput(BrowserView):

    def __call__(self):
        title = self.request.form.get('item_title')
        portal = api.portal.get()
        api.content.create(
            type='Outputdefaults',
            title=title,
            title_es=title,
            title_fr=title,
            container=portal.config.outputs,
            safe_id=True)
        return 'Ok! Default Output created'


class addMainObstaclesTitle(BrowserView):

    def __call__(self):
        title = self.request.form.get('item_title')
        portal = api.portal.get()
        api.content.create(
            type='Mainobstacles',
            title=title,
            title_es=title,
            title_fr=title,
            container=portal.config.outputs,
            safe_id=True)
        return 'Ok! Main obstacle created'


class addMainContributingTitle(BrowserView):

    def __call__(self):
        title = self.request.form.get('item_title')
        portal = api.portal.get()
        api.content.create(
            type='Maincontributing',
            title=title,
            title_es=title,
            title_fr=title,
            container=portal.config.outputs,
            safe_id=True)
        return 'Ok! Main contributing created'


class addTitleKPI(BrowserView):

    def __call__(self):
        title = self.request.form.get('item_title')
        portal = api.portal.get()
        api.content.create(
            type='Outcomedefaults',
            title=title,
            title_es=title,
            title_fr=title,
            container=portal.config.outcomes,
            safe_id=True)
        return 'Ok! Default Outcome created'


class addOutcomeCCS(BrowserView):

    def __call__(self):
        title = self.request.form.get('item_title')
        title_es = self.request.form.get('item_title_es')
        title_fr = self.request.form.get('item_title_fr')
        item_path = self.request.form.get('item_path')
        year = self.request.form.get('year')
        container = api.content.find(path=item_path, depth=0)[0]
        specific_obj = api.content.create(
            type='OutcomeCCS',
            title=title,
            title_es=title_es,
            title_fr=title_fr,
            short_category='other',
            container=container.getObject())

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        generic = annotations[KEY]['generic']
        specifics = annotations[KEY]['specifics']
        monitoring = annotations[KEY]['monitoring']

        outcomeccspecific_info = dict(
            id_specific=specific_obj.id,
            title_specific=specific_obj.title,
            title_specific_es=specific_obj.title_es,
            title_specific_fr=specific_obj.title_fr,
            description=specific_obj.description,
            url='/'.join(specific_obj.getPhysicalPath()),
            selected_specific='',
            icon_url='++theme++gwopa.theme/assets/images/others.png',
            icon_url_selected='++theme++gwopa.theme/assets/images/w-others.png',
            short_category='other',
            baseline=specific_obj.baseline,
            baseline_date=specific_obj.baseline_date,
            objective=specific_obj.objective,
            objective_date=specific_obj.objective_date,
        )
        specifics.append(outcomeccspecific_info)
        outcomeccmonitoring_info = dict(
            id_specific=specific_obj.id,
            title_specific=specific_obj.title,
            title_specific_es=specific_obj.title_es,
            title_specific_fr=specific_obj.title_fr,
            description=specific_obj.description,
            url='/'.join(specific_obj.getPhysicalPath()),
            selected_specific='',
            icon_url='++theme++gwopa.theme/assets/images/others.png',
            icon_url_selected='++theme++gwopa.theme/assets/images/w-others.png',
            icon_basic='++theme++gwopa.theme/assets/images/g-others.png',
            short_category='other',
            baseline=specific_obj.baseline,
            baseline_date=specific_obj.baseline_date,
            objective=specific_obj.objective,
            objective_date=specific_obj.objective_date,
            degree_changes=specific_obj.degree_changes,
            contributed_project=specific_obj.contributed_project,
            contributing_factors=specific_obj.contributing_factors,
            obstacles=specific_obj.obstacles,
            consensus=specific_obj.consensus,
            explain=specific_obj.explain,
            selected_monitoring='notset',
        )
        monitoring.append(outcomeccmonitoring_info)
        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        annotations[KEY] = data
        return 'Ok! Specific Outcomeccs created'


class addOutcomeCCSMonitoring(BrowserView):

    def __call__(self):
        title = self.request.form.get('item_title')
        title_es = self.request.form.get('item_title_es')
        title_fr = self.request.form.get('item_title_fr')
        item_path = self.request.form.get('item_path')
        year = self.request.form.get('year')
        container = api.content.find(path=item_path, depth=0)[0]
        specific_obj = api.content.create(
            type='OutcomeCCS',
            title=title,
            title_es=title_es,
            title_fr=title_fr,
            container=container.getObject())

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        generic = annotations[KEY]['generic']
        specifics = annotations[KEY]['specifics']
        monitoring = annotations[KEY]['monitoring']
        outcomeccmonitoring_info = dict(
            id_specific=specific_obj.id,
            title_specific=specific_obj.title,
            title_specific_es=specific_obj.title_es,
            title_specific_fr=specific_obj.title_fr,
            description='',
            url='/'.join(specific_obj.getPhysicalPath()),
            selected_specific='',
            icon_url='++theme++gwopa.theme/assets/images/others.png',
            icon_url_selected='++theme++gwopa.theme/assets/images/w-others.png',
            icon_basic='++theme++gwopa.theme/assets/images/g-others.png',
            short_category='other',
            baseline='',
            baseline_date='',
            objective='',
            objective_date='',
            degree_changes='',
            contributed_project='',
            contributing_factors='',
            obstacles='',
            consensus='',
            explain='',
            selected_monitoring='notset',
        )
        monitoring.append(outcomeccmonitoring_info)
        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        annotations[KEY] = data
        return 'Ok! Specific Outcomeccs created'


class Create(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        item = api.content.find(path=self.request.form.get('item_path'), depth=0)[0]
        title = self.request.form.get('item_title')
        portal_type = self.request.form.get('item_type')
        obj = api.content.create(
            title=title,
            type=portal_type,
            container=item.getObject())
        obj.description = self.request.form.get('item_description')
        obj.means = self.request.form.get('item_means')
        # obj.risks = self.request.form.get('item_risks')
        members = []
        if (self.request.form.get('item_responsible') is not ''):
            users = self.request.form.get('item_responsible').split(',')
            if isinstance(users, (str,)):
                members.append(users)
            else:
                for member in users:
                    members.append(member)
            obj.members = members

        if portal_type == 'Activity':
            obj.budget = self.request.form.get('item_budget')
            date_start = self.request.form.get('item_start')

            if date_start:
                obj.start = datetime.datetime.strptime(date_start, '%Y-%m-%d')
                date_end = self.request.form.get('item_end')
            if date_end:
                obj.end = datetime.datetime.strptime(date_end, '%Y-%m-%d')
            obj.initial_situation = self.request.form.get('item_initialdescription')
            obj.currency = self.request.form.get('item_hidden_project_currency')
            obj.project_dates = _(u"The dates must be between the limits of this Project. Start: ") + self.request.form.get('item_project_start') + _(u" End: ") + self.request.form.get('item_project_end')
            annotations = IAnnotations(obj)
            for x in range(0, 11):  # Create 11 annotations
                data = dict(real='', planned='', monitoring='')
                KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
                annotations[KEY] = data

        if portal_type == 'Output':
            date_end = self.request.form.get('item_date')
            if date_end:
                obj.end = datetime.datetime.strptime(date_end, '%d %B, %Y')
            obj.measuring_unit = self.request.form.get('item_unit')

        if portal_type == 'OutcomeZONE':
            obj.baseline = self.request.form.get('item_baseline')
            itemdate = self.request.form.get('item_date')
            if itemdate:
                obj.baseline_date = datetime.datetime.strptime(itemdate, '%Y-%m-%d')
            # obj.measuring_frequency = self.request.form.get('item_frequency')
            obj.measuring_unit = self.request.form.get('item_unit')
            obj.zone = self.request.form.get('item_zone')

        if (portal_type == 'Output') or (portal_type == 'OutcomeZONE'):
            annotations = IAnnotations(obj)
            for x in range(0, 11):  # Create 10 annotations
                target = self.request.form.get('item_target' + str(x + 1))
                monitoring_info = dict(
                    progress='',
                    explanation='',
                    obstacles='',
                    contributing='',
                    consideration='',
                    limiting='',
                    updated='',
                )
                data = dict(real='', planned=target, monitoring=monitoring_info)
                KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
                annotations[KEY] = data
        obj.reindexObject()
        return 'Ok, item created'


class ChangeTargetMonitoring(BrowserView):
    """ /changeTarget Change the real value of an element """

    def __call__(self):
        year = self.request.form['pk']
        item_path = self.request.form['name']
        new_value = self.request.form['value']
        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        planned = annotations[KEY]['planned']
        monitoring = annotations[KEY]['monitoring']
        monitoring['progress'] = new_value
        monitoring['updated'] = 'true'
        data = dict(real=new_value, planned=planned, monitoring=monitoring)
        annotations[KEY] = data
        return "OK, value changed"


class ChangeTargetPlanning(BrowserView):
    """ /changeTarget Change the planned value of an element """

    def __call__(self):
        year = self.request.form['pk']
        item_path = self.request.form['name']
        new_value = self.request.form['value']
        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        real = annotations[KEY]['real']
        monitoring = annotations[KEY]['monitoring']
        data = dict(real=real, planned=new_value, monitoring=monitoring)
        annotations[KEY] = data
        return "OK, value changed"


class Update(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['path']
        progress = self.request.form['progress']
        explanation = self.request.form['explanation']
        obstacles = self.request.form['obstacles']
        contributing = self.request.form['contributing']
        consideration = self.request.form['consideration']
        limiting = self.request.form['limiting']
        updated = self.request.form['updated']
        monitoring_info = dict(
            progress=progress,
            explanation=explanation,
            obstacles=obstacles,
            contributing=contributing,
            consideration=consideration,
            limiting=limiting,
            updated=updated,
        )
        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        real = progress
        planned = annotations[KEY]['planned']
        data = dict(real=real, planned=planned, monitoring=monitoring_info)
        annotations[KEY] = data

        return 'Ok, item updated'


class UpdateOutput(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        title = self.request.form['title']
        description = self.request.form['description']
        unit = self.request.form['unit']
        completation_date = self.request.form['completation_date']
        means = self.request.form['means']
        # risks = self.request.form['risks']
        responsible = self.request.form['responsible']


        result = api.content.find(path=self.request.form.get('item_path'), depth=0)[0]
        item = result.getObject()
        item.title = title
        item.description = description
        item.project_dates = ''
        item.measuring_unit = unit
        item.end = datetime.datetime.strptime(completation_date, '%Y-%m-%d')
        item.means = means
        # item.risks = risks
        item.members = responsible
        item.reindexObject()

        new_value = self.request.form['target_value']

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        annotations = IAnnotations(item)
        real = annotations[KEY]['real']
        monitoring = annotations[KEY]['monitoring']
        data = dict(real=real, planned=new_value, monitoring=monitoring)
        annotations[KEY] = data

        return 'Ok, item updated'


class UpdateKPIZone(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        zone = self.request.form['zone']
        responsible = self.request.form['responsible']
        description = self.request.form['description']
        base_value = self.request.form['base_value']
        base_date = self.request.form['base_date']
        unit = self.request.form['unit']
        means = self.request.form['means']
        # risks = self.request.form['risks']

        result = api.content.find(path=self.request.form.get('item_path'), depth=0)[0]
        item = result.getObject()
        item.zone = zone
        item.members = responsible
        item.description = description
        item.baseline = base_value
        item.baseline_date = datetime.datetime.strptime(base_date, '%Y-%m-%d')
        item.measuring_unit = unit
        item.means = means
        # item.risks = risks
        item.reindexObject()

        new_value = self.request.form['target_value']

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        annotations = IAnnotations(item)
        real = annotations[KEY]['real']
        monitoring = annotations[KEY]['monitoring']
        data = dict(real=real, planned=new_value, monitoring=monitoring)
        annotations[KEY] = data

        return 'Ok, item updated'


class UpdateOutcomeCC(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        description = self.request.form['description']
        baseline = self.request.form['baseline']
        baseline_date = self.request.form['baseline_date']
        objective = self.request.form['objective']
        objective_date = self.request.form['objective_date']

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        generic = annotations[KEY]['generic']
        generic[0]['description'] = description
        generic[0]['baseline'] = baseline
        generic[0]['baseline_date'] = baseline_date
        generic[0]['objective'] = objective
        generic[0]['objective_date'] = objective_date
        generic[0]['stage'] = ''

        specifics = annotations[KEY]['specifics']
        monitoring = annotations[KEY]['monitoring']
        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        annotations[KEY] = data

        return 'Ok, item updated'


class UpdateOutcomeCCS(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        # description = self.request.form['description']
        baseline = self.request.form['baseline']
        baseline_date = self.request.form['baseline_date']
        objective = self.request.form['objective']
        objective_date = self.request.form['objective_date']
        id_specific = self.request.form['id_specific']

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        specifics = annotations[KEY]['specifics']
        for specific in specifics:
            if specific['id_specific'] == id_specific:
                # specific['description'] = description
                specific['baseline'] = baseline
                specific['baseline_date'] = baseline_date
                specific['objective'] = objective
                specific['objective_date'] = objective_date
                specific['selected_specific'] = 'selected'
        monitoring = annotations[KEY]['monitoring']
        for specific in monitoring:
            if specific['id_specific'] == id_specific:
                # specific['description'] = description
                specific['baseline'] = baseline
                specific['baseline_date'] = baseline_date
                specific['objective'] = objective
                specific['objective_date'] = objective_date
                specific['selected_specific'] = 'selected'

        generic = annotations[KEY]['generic']
        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        annotations[KEY] = data
        return 'Ok, item updated'


class UpdateOutcomeCCSMonitoring(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        # description = self.request.form['description']
        # baseline = self.request.form['baseline']
        # baseline_date = self.request.form['baseline_date']
        # objective = self.request.form['objective']
        # objective_date = self.request.form['objective_date']
        id_specific = self.request.form['id_specific']
        degree_changes = self.request.form['degree_changes']
        contributed_project = self.request.form['contributed_project']
        consensus = self.request.form['consensus']
        obstacles = self.request.form['obstacles']
        contributing_factors = self.request.form['contributing_factors']
        explain = self.request.form['explain']

        degree_values = {'-2': 'verybad', '-1': 'bad', '0': 'equal', '1': 'good', '2': 'verygood'}

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        specifics = annotations[KEY]['specifics']
        for specific in specifics:
            if specific['id_specific'] == id_specific:
                # specific['description'] = description
                # specific['baseline'] = baseline
                # specific['baseline_date'] = baseline_date
                # specific['objective'] = objective
                # specific['objective_date'] = objective_date
                specific['selected_specific'] = 'selected'
        monitoring = annotations[KEY]['monitoring']
        for specific in monitoring:
            if specific['id_specific'] == id_specific:
                # specific['description'] = description
                # specific['baseline'] = baseline
                # specific['baseline_date'] = baseline_date
                # specific['objective'] = objective
                # specific['objective_date'] = objective_date
                specific['selected_specific'] = 'selected'
                specific['degree_changes'] = degree_changes
                specific['contributed_project'] = contributed_project
                specific['consensus'] = consensus
                specific['obstacles'] = obstacles
                specific['contributing_factors'] = contributing_factors
                specific['explain'] = explain
                val_degree_changes = degree_changes[0]
                if val_degree_changes == '-':
                    val_degree_changes = degree_changes[0:2]
                specific['selected_monitoring'] = degree_values[val_degree_changes]
        generic = annotations[KEY]['generic']
        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        annotations[KEY] = data
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'result': 'OK',
                           'degree_changes_text': getTranslatedDegreeChangesFromID(degree_changes),
                           'contributed_project_text': getTranslatedContributedProjectFromID(contributed_project),
                           'consensus_text': getTranslatedConsensusFromID(consensus),
                           'contributing_factors': json.dumps(getDictTranslatedContributingFromList(contributing_factors)),
                           'obstacles': json.dumps(getDictTranslatedObstaclesFromList(obstacles))})


class UpdateStageMonitoring(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        stage = self.request.form['stage']

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        generic = annotations[KEY]['generic']
        generic[0]['stage'] = stage

        specifics = annotations[KEY]['specifics']
        monitoring = annotations[KEY]['monitoring']
        data = dict(real='', planned='', monitoring=monitoring, generic=generic, specifics=specifics)
        annotations[KEY] = data

        return 'Ok, item updated'

class updatePartnership(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['item_path']
        overall_score = self.request.form['overall_score']
        improvement_needed = self.request.form['improvement_needed']
        # suggestions_improve = self.request.form['suggestions_improve']

        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        annotations[KEY]['partnerships']['overall_score'] = overall_score
        annotations[KEY]['partnerships']['improvement_needed'] = improvement_needed
        # annotations[KEY]['partnerships']['suggestions_improve'] = suggestions_improve
        annotations[KEY]['partnerships']['suggestions_improve'] = ''
        data = dict(partnerships=annotations[KEY]['partnerships'])
        annotations[KEY] = data
        return 'Ok, item updated'


class getProjectWOPPlatform(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []

        wop_platform = []
        for item in items:
            value = item.getObject().wop_platform
            if value and value not in wop_platform:
                wop_platform.append(value)
        wop_platform.sort()

        for value in wop_platform:
            results.append(dict(
                id=value,
                text=value))

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectWOPProgram(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []

        wop_program = []
        for item in items:
            value = item.getObject().wop_program
            if value and value not in wop_program:
                wop_program.append(value)
        wop_program.sort()

        for value in wop_program:
            results.append(dict(
                id=value,
                text=value))

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectWorkingArea(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []
        areas = []
        for item in items:
            values = item.getObject().areas
            if values:
                for value in values:
                    if value not in areas:
                        areas.append(value)
        areas.sort()
        for value in areas:
            results.append(dict(
                id=value,
                text=value))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectCountry(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []
        countries = []
        for item in items:
            value = item.getObject().country
            if value:
                if value not in countries:
                    countries.append(value)
        countries.sort()
        for value in countries:
            results.append(dict(
                id=value,
                text=value))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectPartners(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []
        partners = []
        for item in items:
            values = item.getObject().partners
            if values:
                for value in values:
                    if value not in partners:
                        partners.append(value)
        partners.sort()
        for value in partners:
            results.append(dict(
                id=value,
                text=value))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectTags(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []
        tags = []
        for item in items:
            values = item.getObject().category
            if values:
                for value in values:
                    if value not in tags:
                        tags.append(value)
        tags.sort()
        for value in tags:
            results.append(dict(
                id=value,
                text=value))

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectDates(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []
        dates = []
        for item in items:
            obj = item.getObject()
            start = obj.startactual.year
            end = obj.completionactual.year
            numbers = range(start, end + 1)
            if numbers:
                for value in numbers:
                    if value not in dates:
                        dates.append(value)
        dates.sort()
        for value in dates:
            results.append(dict(
                id=str(value),
                text=str(value)))

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class getProjectKPIs(BrowserView):

    def __call__(self):
        items = api.content.find(portal_type="Project")
        results = []
        values = []
        for item in items:
            obj = item.getObject()
            elements = api.content.find(portal_type=['OutcomeZONE'], context=obj, depth=1)
            kpis = []
            for kpi in elements:
                kpis.append(kpi.Title)
            if kpis:
                for value in kpis:
                    if value not in values:
                        values.append(value)
        values.sort()
        for value in values:
            results.append(dict(
                id=value,
                text=value))

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps({'results': results})


class allProjectsMap(BrowserView):
    # Returns all projects to make queries in global map selectors - allProjects.json #
    def __call__(self):
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            obj = item.getObject()
            if obj.longitude and obj.latitude:
                if obj.total_budget:
                    budget = int(obj.total_budget)
                else:
                    budget = 0
                if not obj.areas:
                    areas = []
                else:
                    areas = obj.areas
                if not obj.wop_platform:
                    wop_platform = []
                else:
                    wop_platform = obj.wop_platform
                if not obj.wop_program:
                    wop_program = []
                else:
                    wop_program = obj.wop_program
                if not obj.category:
                    category = []
                else:
                    category = obj.category
                if not obj.partners:
                    partners = []
                else:
                    partners = obj.partners
                start = obj.startactual.year
                end = obj.completionactual.year
                years = range(start, end + 1)
                years = map(str, years)
                elements = api.content.find(portal_type=['OutcomeZONE'], context=obj, depth=1)
                kpis = []
                for kpi in elements:
                    kpis.append(kpi.Title)
                if obj.project_manager_admin:
                    responsible = obj.project_manager_admin
                else:
                    responsible = None
                if not responsible:
                    popup = '<a href="' + obj.absolute_url() + '">' + obj.title + '</a>'
                else:
                    user = api.user.get(username=responsible)
                    if user:
                        responsible = user.getProperty('fullname')
                    popup = '<a href="' + obj.absolute_url() + '">' + obj.title + '</a><br/>' + str(responsible)

                try:
                    poi = Feature(
                        geometry=Point((float(obj.longitude), float(obj.latitude))),
                        properties={
                            'title': obj.title,
                            'popup': popup,
                            'total_budget': budget,
                            'wop_program': wop_program,
                            'wop_platform': wop_platform,
                            'partners': partners,
                            'country': obj.country,
                            'tags': category,
                            'areas': areas,
                            'years': years,
                            'kpis': kpis})
                    results.append(poi)
                except:
                    pass
        obj = ({"type": "FeatureCollection", 'features': results})
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(obj)


class activeProjectsMap(BrowserView):
    # Returns Active projects to show in layer map - activeProjects.json#
    def __call__(self):
        today = datetime.date.today()
        items = api.content.find(portal_type=['Project'])
        results = []
        for item in items:
            obj = item.getObject()
            if obj.project_manager_admin:
                responsible = obj.project_manager_admin
            else:
                responsible = None
            # Add only current date projects
            if (obj.startactual <= today <= obj.completionactual):
                if obj.longitude and obj.latitude:
                    if not responsible:
                        popup = '<a href="' + obj.absolute_url() + '">' + obj.title + '</a><br/>'
                    else:
                        user = api.user.get(username=responsible)
                        if user:
                            responsible = user.getProperty('fullname')
                        popup = '<a href="' + obj.absolute_url() + '">' + obj.title + '</a><br/>' + str(responsible)
                    poi = Feature(
                        geometry=Point((float(obj.longitude), float(obj.latitude))),
                        properties={
                            'title': obj.title,
                            'popup': popup})
                    results.append(poi)
        obj = ({"type": "FeatureCollection", 'features': results})
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(obj)


class inactiveProjectsMap(BrowserView):
    # Returns Inactive projects to show in layer map - inactiveProjects.json #
    def __call__(self):
        today = datetime.date.today()
        items = api.content.find(portal_type=['Project'])

        results = []
        for item in items:
            obj = item.getObject()
            if obj.project_manager_admin:
                responsible = obj.project_manager_admin
            else:
                responsible = None
            # Add only passed or not started projects
            if ((obj.startactual < today) and (obj.completionactual < today)) or ((obj.startactual > today) and (obj.completionactual > today)):
                if obj.longitude and obj.latitude:
                    if not responsible:
                        popup = '<a href="' + obj.absolute_url() + '">' + obj.title + '</a><br/>'
                    else:
                        user = api.user.get(username=responsible)
                        if user:
                            responsible = user.getProperty('fullname')
                        popup = '<a href="' + obj.absolute_url() + '">' + obj.title + '</a><br/>' + str(responsible)
                    poi = Feature(
                        geometry=Point((float(obj.longitude), float(obj.latitude))),
                        properties={
                            'title': obj.title,
                            'popup': popup})
                    results.append(poi)
        obj = ({"type": "FeatureCollection", 'features': results})
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(obj)
