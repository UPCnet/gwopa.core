# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView

from plone import api
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.annotation.interfaces import IAnnotations

from gwopa.core.utils import percentage
from gwopa.core.utils import getTranslatedMesuringUnitFromID

import datetime
import json
import math


class GetDashboard(BrowserView):
    """Service for list activities and outputs from WA and year."""

    # /api-getDashboard
    def __call__(self):
        """Answer for the webservice."""
        wa_path = self.request.form.get('wa', False)
        year = self.request.form.get('year', False)

        if not wa_path:
            BadRequest('Working area are required')
        if not year:
            BadRequest('Year are required')

        indicators = {}
        if wa_path:
            data_year = self.context.gwopa_year_phases[int(year) - 1]
            start = datetime.datetime.strptime(data_year['start_iso'], '%Y-%m-%d')
            end = datetime.datetime.strptime(data_year['end_iso'], '%Y-%m-%d')

            # Los de la fase [---]
            range_start = {'query': (start, end), 'range': 'min:max'}
            range_end = {'query': (start, end), 'range': 'min:max'}
            activities1 = api.content.find(
                portal_type=['Activity'],
                start=range_start,
                end=range_end,
                path={'query': wa_path, 'depth': 1})

            # Los de fuera de la fase start y end ---][----
            range_start = {'query': (start), 'range': 'max'}
            range_end = {'query': (end), 'range': 'min'}
            activities2 = api.content.find(
                portal_type=['Activity'],
                start=range_start,
                end=range_end,
                path={'query': wa_path, 'depth': 1})

            # Los que empiezan antes y acaban en fase ---]
            ranges = {'query': (start), 'range': 'max'}
            range_end = {'query': (start, end), 'range': 'min:max'}

            activities3 = api.content.find(
                portal_type=['Activity'],
                start=ranges,
                end=range_end,
                path={'query': wa_path, 'depth': 1})

            # Los que empiezan aqui y acaban despues [----
            range_start = {'query': (start, end), 'range': 'min:max'}
            range_end = {'query': (end), 'range': 'min'}
            activities4 = api.content.find(
                portal_type=['Activity'],
                start=range_start,
                end=range_end,
                path={'query': wa_path, 'depth': 1})

            items = activities1 + activities2 + activities3 + activities4

            for act in items:
                indicators[act.Title] = {}
                annotations = IAnnotations(act.getObject())
                KEY = "GWOPA_TARGET_YEAR_" + str(year)
                if annotations[KEY]['monitoring'] == '' or annotations[KEY]['monitoring']['progress'] == '':
                    value = 0
                else:
                    value = annotations[KEY]['monitoring']['progress']
                indicators[act.Title]['activity_val'] = (value)
                indicators[act.Title]['outputs'] = {}
                outputs = api.content.find(
                    portal_type=['Output'],
                    path={'query': act.getPath(), 'depth': 1})
                for output in outputs:
                    measuring_unit = getTranslatedMesuringUnitFromID(output.getObject().measuring_unit)
                    annotations = IAnnotations(output.getObject())
                    KEY = "GWOPA_TARGET_YEAR_" + str(year)
                    if annotations[KEY]['planned'] == '' or annotations[KEY]['monitoring'] == '' or annotations[KEY]['monitoring']['progress'] == '':
                        value = "0 " + measuring_unit
                    else:
                        planned = annotations[KEY]['planned']
                        real = annotations[KEY]['monitoring']['progress']
                        # value = percentage(real, planned)
                        value = "" + str(real) + '/' + str(planned) + " " + measuring_unit
                    indicators[act.Title]['outputs'][output.Title] = value

            self.request.response.setHeader("Content-type", "application/json")
            return json.dumps(indicators)
        else:
            return None


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


class GetPerformance(BrowserView):
    """Service for list activities from WA and year."""
    # /api-getPerformance

    def __call__(self):
        """Answer for the webservice."""
        path = self.request.form.get('performance', False)
        if not path:
            BadRequest('Performance are required')

        projectFolder = '/'.join(path.split('/')[0:-1])
        performanceID = path.split('/')[-1]

        kpi = api.content.find(
            id=performanceID,
            portal_type=['OutcomeZONE'],
            path={'query': projectFolder, 'depth': 1})

        if not kpi:
            BadRequest('KPI error')

        project = api.content.find(
            id=projectFolder.split('/')[-1],
            portal_type=['Project'],
            path={'query': '/'.join(projectFolder.split('/')[0:-1]), 'depth': 1})

        if not project:
            BadRequest('Project error')

        kpi = kpi[0].getObject()
        project = project[0].getObject()

        projectPhases = len(project.gwopa_year_phases)
        annotations = IAnnotations(kpi)

        series = [{"name": "", "data": []}, {"name": "", "data": []}]
        xaxis = []
        maxYaxis = 0
        for x in range(0, projectPhases):
            KEY = "GWOPA_TARGET_YEAR_" + str(x + 1)
            info = annotations[KEY]

            real = 0 if not info['real'] or info['real'] == '' else int(info['real'])
            planned = 0 if not info['planned'] or info['planned'] == '' else int(info['planned'])

            series[0]['data'].append(planned)
            series[1]['data'].append(real)
            xaxis.append(project.gwopa_year_phases[x]['start'][-4:])

            maxYaxis = real if real > maxYaxis else maxYaxis
            maxYaxis = planned if planned > maxYaxis else maxYaxis

        if maxYaxis <= 10:
            maxYaxis = 10
        elif maxYaxis <= 100:
            maxYaxis = int(math.ceil(maxYaxis / float(10))) * 10
        else:
            maxYaxis = int(math.ceil(maxYaxis / float(100))) * 100

        data = {
            "series": series,
            "xaxis": xaxis,
            "maxYaxis": maxYaxis,
            "mesuring_unit": getTranslatedMesuringUnitFromID(kpi.measuring_unit),
        }

        return json.dumps(data)
