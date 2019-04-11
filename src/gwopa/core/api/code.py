# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
import json
from plone import api


class getPhases(BrowserView):

    def __call__(self):
        project = self.context
        results = []
        results = [{'phases': len(project.gwopa_fases),
                    'gwopa_fases': project.gwopa_fases,
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
        item = self.request.form.get('item')
        return item
