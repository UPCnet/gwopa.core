# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone import api
from zope.component import ComponentLookupError
from zExceptions import BadRequest
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.annotation.interfaces import IAnnotations
import json
from gwopa.core.utils import percentage


class GetActivities(BrowserView):
    """Service for list activities from WA and year."""
    # /api-getActivities

    def __call__(self):
        """Answer for the webservice."""
        wa_path = self.request.form.get('wa', False)
        year = self.request.form.get('year', False)
        if not wa_path:
            BadRequest('Working area are required')
        if not year:
            BadRequest('Year are required')

        items = api.content.find(
            portal_type=['Activity'],
            path={'query': wa_path, 'depth': 1})
        titles = []
        values = [{'data': []}]
        for item in items:
            titles.append(item.Title)
            annotations = IAnnotations(item.getObject())
            KEY = "GWOPA_TARGET_YEAR_" + str(year)
            if annotations[KEY]['monitoring'] == '' or annotations[KEY]['monitoring']['progress'] == '':
                value = 0
            else:
                value = annotations[KEY]['monitoring']['progress']
            values[0]['data'].append(value)

        results = []
        results.append(titles)
        results.append(values)
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class GetOutputs(BrowserView):
    """Service for list outputs from WA and year."""

    def __call__(self):
        """Answer for the webservice."""
        wa_path = self.request.form.get('wa', False)
        year = self.request.form.get('year', False)
        if not wa_path:
            BadRequest('Working area are required')
        if not year:
            BadRequest('Year are required')

        results = []
        titles = []
        values = [{'data': []}]
        activities = api.content.find(
            portal_type=['Activity'],
            path={'query': wa_path, 'depth': 1})
        for act in activities:
            outputs = api.content.find(
                portal_type=['Output'],
                path={'query': act.getPath(), 'depth': 1})
            for output in outputs:
                titles.append(output.Title)
                annotations = IAnnotations(output.getObject())
                KEY = "GWOPA_TARGET_YEAR_" + str(year)
                if annotations[KEY]['planned'] == '' or annotations[KEY]['monitoring'] == '' or annotations[KEY]['monitoring']['progress'] == '':
                    value = 0
                else:
                    planned = annotations[KEY]['planned']
                    real = annotations[KEY]['monitoring']['progress']
                    value = percentage(real, planned)
                values[0]['data'].append(value)

        results.append(titles)
        results.append(values)
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class GetCapacityChanges(Service):
    """Sevice for list groups linked to user."""

    def reply(self):
        """Answer for the webservice."""
        # user = self.request.form.get('user', False)
        # if not user:
        #     BadRequest('User are required')
        #
        # mt = getToolByName(self, 'portal_membership')
        # if mt.getMemberById(user) is None:
        #     return self._error(
        #         404, "Not Found",
        #         "The user '{}' was deleted and currently does not exist".format(user)
        #     )
        #
        # try:
        #     username = api.user.get(username=user)
        # except ComponentLookupError:
        #     return self._error(
        #         404, "Not Found",
        #         "The user '{}' does not exist".format(user)
        #     )
        #
        # groups = api.group.get_groups(user=username)
        #
        # return [g.id for g in groups]
