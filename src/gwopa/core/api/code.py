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
        portal_type = self.request.form.get('item_type')
        obj = api.content.create(
            title=title,
            type=portal_type,
            container=item.getObject())
        obj.description = self.request.form.get('item_description')
        obj.initial_situation = self.request.form.get('item_baseline')
        obj.baseline = self.request.form.get('item_baseline')
        obj.measuring_unit = self.request.form.get('item_unit')
        obj.measuring_frequency = self.request.form.get('item_frequency')
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
        annotations = IAnnotations(obj)
        for x in range(0, 11):  # Create 10 annotations
            target = self.request.form.get('item_target' + str(x + 1))
            data = dict(real='', planned=target)
            KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
            annotations[KEY] = data

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
        data = dict(planned=new_value)
        annotations[KEY] = data
        return "OK, value changed"
