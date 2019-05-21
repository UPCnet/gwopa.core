# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import json
from plone import api
from decimal import Decimal
from operator import itemgetter
from zope.annotation.interfaces import IAnnotations
import datetime
from gwopa.core import _


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
        literals = sorted(literals, key=itemgetter('Title'), reverse=False)
        for item in literals:
            results.append(dict(
                name=item.Title))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getMainContributing(BrowserView):
    # /api-getMainContributing
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Maincontributing')
        literals = sorted(literals, key=itemgetter('Title'), reverse=False)
        for item in literals:
            results.append(dict(
                name=item.Title))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getOutcomes(BrowserView):
    # /api-getOutcomes
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Outcomedefaults')
        literals = sorted(literals, key=itemgetter('Title'), reverse=False)
        for item in literals:
            results.append(dict(
                name=item.Title))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getUsers(BrowserView):

    def __call__(self):
        results = []
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

        results = []
        item = api.content.find(portal_type="SettingsPage", id='settings')
        if item:
            values = item[0].getObject().measuring_unit
            terms = []
            for value in values.split('\n'):
                if value != '':
                    terms.append(value)
        terms.sort()
        for item in terms:
            results.append(dict(
                name=item))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getFrequency(BrowserView):
    # /api-getFrequency
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        item = api.content.find(portal_type="SettingsPage", id='settings')
        if item:
            values = item[0].getObject().measuring_frequency
            terms = []
            for value in values.split('\n'):
                if value != '':
                    terms.append(value)
        terms.sort()
        for item in terms:
            results.append(dict(
                name=item))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


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
        title = self.request.form.get('item_title')
        portal_type = self.request.form.get('item_type')
        obj = api.content.create(
            title=title,
            type=portal_type,
            container=item.getObject())

        obj.incash = Decimal(self.request.form.get('item_incash').replace(',', ''))
        obj.inkind = Decimal(self.request.form.get('item_inkind').replace(',', ''))

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
        return 'Ok, Outputdefaults created'


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
        return 'Ok, Mainobstacles created'


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
        return 'Ok, Maincontributing created'


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
        return 'Ok, Outcomedefaults created'


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
        obj.risks = self.request.form.get('item_risks')
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
                obj.start = datetime.datetime.strptime(date_start, '%Y-%m-%d').date()
                date_end = self.request.form.get('item_end')
            if date_end:
                obj.end = datetime.datetime.strptime(date_end, '%Y-%m-%d').date()
            obj.initial_situation = self.request.form.get('item_initialdescription')
            obj.currency = self.request.form.get('item_hidden_project_currency')
            obj.project_dates = 'Start date: ' + self.request.form.get('item_project_start') + ' - End date: ' + self.request.form.get('item_project_end')
            annotations = IAnnotations(obj)
            for x in range(0, 11):  # Create 10 annotations
                data = dict(real='', planned='', monitoring='')
                KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
                annotations[KEY] = data

        if portal_type == 'Output':
            date_end = self.request.form.get('item_date')
            if date_end:
                obj.end = datetime.datetime.strptime(date_end, '%d %B, %Y').date()
            obj.measuring_unit = self.request.form.get('item_unit')

        if (portal_type == 'OutcomeKPI') or (portal_type == 'OutcomeZONE'):
            obj.baseline = self.request.form.get('item_baseline')
            itemdate = self.request.form.get('item_date')
            if itemdate:
                obj.baseline_date = datetime.datetime.strptime(itemdate, '%Y-%m-%d').date()
            obj.measuring_frequency = self.request.form.get('item_frequency')
            obj.measuring_unit = self.request.form.get('item_unit')
            obj.zone = self.request.form.get('item_zone')

        if (portal_type == 'Output') or (portal_type == 'OutcomeZONE') or (portal_type == 'OutcomeKPI'):
            annotations = IAnnotations(obj)
            for x in range(0, 11):  # Create 10 annotations
                target = self.request.form.get('item_target' + str(x + 1))
                data = dict(real='', planned=target, monitoring='')
                KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
                annotations[KEY] = data

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
        data = dict(real=new_value, planned=planned, monitoring='')
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
        data = dict(real=real, planned=new_value, monitoring='')
        annotations[KEY] = data
        return "OK, value changed"


class Update(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        year = self.request.form['year']
        item_path = self.request.form['path']
        progress = self.request.form['progress']
        explanation = self.request.form['explanation']
        if self.request.form.get('obstacles[]'):
            obstacles = self.request.form['obstacles[]']
        else:
            obstacles = ''
        if self.request.form.get('contributing[]'):
            contributing = self.request.form['contributing[]']
        else:
            contributing = ''
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
