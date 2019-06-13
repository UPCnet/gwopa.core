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
            BadRequest('Working area is required')
        if not year:
            BadRequest('Year is required')

        if wa_path:
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
        else:
            return None


class GetOutputs(BrowserView):
    """Service for list outputs from WA and year."""

    def __call__(self):
        """Answer for the webservice."""
        wa_path = self.request.form.get('wa', False)
        year = self.request.form.get('year', False)
        #import ipdb; ipdb.set_trace()
        # self.context.gwopa_year_phases[1]
        #{'end': 'June 11, 2021', 'end_iso': '2021-06-11', 'pattern_end': '2021,5,11', 'start': 'June 11, 2020', 'pattern_start': '2020,5,11', 'start_iso': '2020-06-11', 'fase': 2}
        if not wa_path:
            BadRequest('Working area are required')
        if not year:
            BadRequest('Year are required')

        results = []
        titles = []
        values = [{'data': []}]
        if wa_path:
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
        else:
            return None


class GetCapacityChanges(Service):
    """Service for list Capacity Changes from WA and year."""

    def reply(self):
        """Answer for the webservice."""
        wa_path = self.request.form.get('wa', False)
        year = self.request.form.get('year', False)
        if not wa_path:
            BadRequest('Working area are required')
        if not year:
            BadRequest('Year are required')

        results = []
        specifics = []
        others = []
        outcomes = api.content.find(
            portal_type=['OutcomeCC'],
            path={'query': wa_path, 'depth': 1})
        for outcome in outcomes:
            annotations = IAnnotations(outcome.getObject())
            KEY = "GWOPA_TARGET_YEAR_" + str(year)
            if annotations[KEY]['monitoring'] == '' or annotations[KEY]['monitoring'][0]['icon_basic'] == '' or annotations[KEY]['monitoring'][0]['selected_monitoring'] == '':
                pass
            else:
                for specific in annotations[KEY]['monitoring']:
                    if specific['short_category'] == 'other':
                        others.append(dict(
                            id=specific['id_specific'],
                            icon_basic=specific['icon_basic'],
                            icon_url_selected=specific['icon_url_selected'],
                            title_specific=specific['title_specific'],
                            selected_monitoring=specific['selected_monitoring']))
                    else:
                        specifics.append(dict(
                            id=specific['id_specific'],
                            icon_basic=specific['icon_basic'],
                            icon_url_selected=specific['icon_url_selected'],
                            title_specific=specific['title_specific'],
                            selected_monitoring=specific['selected_monitoring']))

        results.append(specifics)
        results.append(others)
        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)


class GetCurrentStage(BrowserView):
    """Service for get current Stage for this WA and year."""

    def __call__(self):
        """Answer for the webservice."""
        wa_path = self.request.form.get('wa', False)
        year = self.request.form.get('year', False)
        if not wa_path:
            BadRequest('Working area are required')
        if not year:
            BadRequest('Year are required')

        results = []
        items = api.content.find(
            portal_type=['OutcomeCC'],
            path={'query': wa_path, 'depth': 1})
        KEY = "GWOPA_TARGET_YEAR_" + str(year)
        for item in items:
            annotations = IAnnotations(item.getObject())
            stage = annotations[KEY]['generic'][0]['stage']
            if stage:
                for i in range(1, 5):
                    if i < int(stage):
                        state = "past"
                    elif i == int(stage):
                        state = "current"
                    else:
                        state = "future"
                    results.append(dict(id="stage-" + str(i),
                                        title="Stage " + str(i),
                                        state=state))
            else:
                for i in range(1, 5):
                    results.append(dict(id="stage-" + str(i),
                                        title="Stage " + str(i),
                                        state="future"))

        self.request.response.setHeader("Content-type", "application/json")
        return json.dumps(results)
