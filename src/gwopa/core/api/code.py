# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides
import json
from plone import api


class getPhases(BrowserView):
    # /api-getphases
    def __call__(self):
        project = self.context
        results = []
        results = [{'phases': len(project.gwopa_year_phases),
                    'gwopa_year_phases': project.gwopa_year_phases,
                    }]
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class getOutputs(BrowserView):
    # /api-getoutputs
    def __call__(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        results = []
        catalog = api.portal.get_tool('portal_catalog')
        literals = catalog.unrestrictedSearchResults(
            portal_type='Outputdefaults')
        cont = 1
        for item in literals:
            results.append(dict(
                id=cont,
                name=item.Title))
            cont = cont + 1
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
        print self.request.form
        title = self.request.form.get('item_title')
        api.content.create(
            title=title,
            type='Outputdefaults',
            container=self.context)
        return 'Ok, item created'
