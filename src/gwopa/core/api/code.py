# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
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
        return json.dumps(results)


class getUsers(BrowserView):

    def __call__(self):
        users = api.user.get_users()
        results = []
        for user in users:
            results.append(dict(
                id=user.id,
                text=user.getProperty('fullname')))
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
        # api.content.delete(obj=obj, check_linkintegrity=False)
        return 'Ok, item deleted'
