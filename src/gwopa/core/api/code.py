# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import json
from plone import api
from operator import itemgetter
from zope.annotation.interfaces import IAnnotations
import datetime


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


class getUsers(BrowserView):

    def __call__(self):
        users = api.user.get_users()
        results = []
        for user in users:
            results.append(dict(
                id=user.id,
                text=user.getProperty('fullname')))
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(
            {
                'placeholder': "Select users...",
                'results': results,
            }
        )


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


class Create(BrowserView):

    def __call__(self):
        # TODO: check permissions. now cmf.ModifyPortalContent
        item = api.content.find(path=self.request.form.get('item_path'), depth=0)[0]
        title = self.request.form.get('item_title')
        obj = api.content.create(
            title=title,
            type='Output',
            container=item.getObject())
        obj.description = self.request.form.get('item_description')
        obj.initial_situation = self.request.form.get('item_baseline')
        obj.measuring_unit = self.request.form.get('item_unit')
        obj.measuring_frequency = self.request.form.get('item_frequency')
        obj.means = self.request.form.get('item_means')
        obj.risks = self.request.form.get('item_risks')
        obj.members = self.request.form.get('item_responsible')
        target1 = self.request.form.get('item_target1')
        target2 = self.request.form.get('item_target2')
        target3 = self.request.form.get('item_target3')
        target4 = self.request.form.get('item_target4')
        KEY1 = "GWOPA_TARGET_YEAR_1"
        KEY2 = "GWOPA_TARGET_YEAR_2"
        KEY3 = "GWOPA_TARGET_YEAR_3"
        KEY4 = "GWOPA_TARGET_YEAR_4"
        annotations = IAnnotations(obj)
        annotations[KEY1] = target1
        annotations[KEY2] = target2
        annotations[KEY3] = target3
        annotations[KEY4] = target4
        date_end = self.request.form.get('item_date')
        if date_end:
            obj.end = datetime.datetime.strptime(date_end, '%Y-%m-%d')
        return 'Ok, item created'


class ChangeTarget(BrowserView):
    """ /changeTarget Change the Target Value of an element """

    def __call__(self):
        year = self.request.form['pk']
        item_path = self.request.form['name']
        new_value = self.request.form['value']
        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        item = api.content.find(path=item_path, depth=0)[0]
        annotations = IAnnotations(item.getObject())
        annotations[KEY] = new_value
        return "OK, value changed"
