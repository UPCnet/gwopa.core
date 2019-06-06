# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
from zope.annotation.interfaces import IAnnotations
#import datetime
from gwopa.core import _


@implementer(IPublishTraverse)
class monitoringView(BrowserView):
    """ Planning View """

    index = ViewPageTemplateFile("templates/monitoring.pt")

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(monitoringView, self).__init__(context, request)
        self.year = None
        path_ordered = request.path[-1:]
        # get all param in the path -> the year /monitoring/2019
        self.year = '/'.join(path_ordered)

    def getYear(self):
        return self.year

    def getFaseStart(self):
        return self.fase_start

    def getFaseEnd(self):
        return self.fase_end

    def projectTitle(self):
        return self.context.title

    def project_currency(self):
        return self.context.currency.split('-')[-1:][0]

    def hidden_project_currency(self):
        currency = getattr(self.context, 'currency', None)
        if currency:
            letter = currency
        else:
            letter = 'USD-Dollar-$'
        return letter

    def getPath(self):
        return '/'.join(self.context.getPhysicalPath())

    def project_start(self):
        start = self.context.startactual.strftime('%Y-%m-%d')
        return start

    def project_end(self):
        end = self.context.completionactual.strftime('%Y-%m-%d')
        return end

    def __call__(self):
        if self.request['URL'].split('/')[-1][0:4] == 'api-':
            self.request.response.redirect(self.request['URL'].replace('monitoring/', ''))
        if (not self.year or self.year == '0'):
            # Empty query or 0 returns default template
            self.year = '1'
            self.fase_start = self.context.gwopa_year_phases[int(self.year) - 1]['start']
            self.fase_end = self.context.gwopa_year_phases[int(self.year) - 1]['end']
            return self.index()
        else:
            try:
                self.year = int(self.year)
            except:
                self.year = 1
            if self.year > len(self.context.gwopa_year_phases):
                self.year = 1
                self.fase_start = self.context.gwopa_year_phases[int(self.year) - 1]['start']
                self.fase_end = self.context.gwopa_year_phases[int(self.year) - 1]['end']
            else:
                self.fase_start = self.context.gwopa_year_phases[int(self.year) - 1]['start']
                self.fase_end = self.context.gwopa_year_phases[int(self.year) - 1]['end']
            return self.index()
        # TODO: if copy or delete make action!

    def getPhases(self):
        return len(self.context.gwopa_year_phases)

    def getItems(self):
        """ Returns all the project years of the monitoring """
        items = len(self.context.gwopa_year_phases)
        results = []
        total = 0

        while total != items:
            if (total == 0) and (self.request.steps[-1] == 'monitoring'):
                classe = 'disabled'
            elif self.request.steps[-1] == str(total + 1):
                classe = 'disabled'
            else:
                classe = 'visible'
            if total == 0:
                url = self.context.absolute_url_path() + '/monitoring/'
            else:
                url = self.context.absolute_url_path() + '/monitoring/' + str(total + 1)
            results.append(dict(
                title=_(u"Project year"),
                year=str(total + 1),
                url=url,
                alt=_(u"Show monitoring of year "),
                classe=classe))
            total = total + 1
        return sorted(results, key=itemgetter('title'), reverse=False)

    def getAreas(self):
        """ Returns all the Improvement Areas in a Project """
        items = api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context)
        results = []
        for project in items:
            item = project.getObject()
            results.append(dict(title=item.title,
                                url='/'.join(item.getPhysicalPath()),
                                id=item.id,
                                description=item.description,
                                portal_type=item.portal_type
                                ))
        return sorted(results, key=itemgetter('title'), reverse=False)

    def indicatorsInside(self, item):
        """ returns objects from first level (elements inside ImprovementArea) """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        data_year = self.context.gwopa_year_phases[int(self.year) - 1]
        # start = datetime.datetime.strptime(data_year['start_iso'], '%Y-%d-%m')
        # end = datetime.datetime.strptime(data_year['end_iso'], '%Y-%d-%m')
        # date_range_query = {'query': (start, end), 'range': 'min:max'},
        # start=date_range_query,
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            path={'query': folder_path,
                  'depth': 1})
        # date_range_query = {'query': (end, end), 'range': 'max'}
        #     end=date_range_query,
        outputs = portal_catalog.unrestrictedSearchResults(
            portal_type=['Output'],
            path={'query': folder_path,
                  'depth': 1})
        items = items + outputs
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in items:
            obj = item.getObject()
            annotations = IAnnotations(obj)
            if KEY in annotations.keys():
                if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
                    target_value_real = ''
                    target_value_planned = _(u"Not defined")
                    monitoring_info = ''
                else:
                    target_value_real = annotations[KEY]['real']
                    target_value_planned = annotations[KEY]['planned']
                    monitoring_info = annotations[KEY]['monitoring']
            else:
                target_value_real = ''
                target_value_planned = '-----'
            if item.portal_type == 'Activity':
                unit = ''
            else:
                unit = obj.measuring_unit
            if not item.start:
                start = '-----'
            else:
                start = item.start.strftime('%Y-%m')
            if not item.end:
                end = '-----'
            else:
                end = item.end.strftime('%Y-%m')
            if monitoring_info == '':
                consideration, explanation, limiting, obstacles, contributing, progress, updated = '', '', '', '', '', '', ''
            else:
                consideration = monitoring_info['consideration'] if monitoring_info.get('consideration') is not None else ''
                explanation = monitoring_info['explanation'] if monitoring_info.get('explanation') is not None else ''
                obstacles = monitoring_info['obstacles'] if monitoring_info.get('obstacles') is not None else ''
                contributing = monitoring_info['contributing'] if monitoring_info.get('contributing') is not None else ''
                limiting = monitoring_info['limiting'] if monitoring_info.get('limiting') is not None else ''
                progress = monitoring_info['progress'] if monitoring_info.get('progress') is not None else ''
                updated = monitoring_info['updated'] if monitoring_info.get('updated') is not None else ''
            results.append(dict(
                title=item.Title,
                path=item.getPath(),
                id=item.id,
                portal_type=item.portal_type,
                start=start,
                end=end,
                unit=unit,
                target_value_real=target_value_real,
                target_value_planned=target_value_planned,
                year=self.year,
                next_update=data_year['end_iso'][0:7],
                consideration=consideration,
                explanation=explanation,
                obstacles=obstacles,
                contributing=contributing,
                limiting=limiting,
                progress=progress,
                updated=updated,
                url='/'.join(obj.getPhysicalPath())))
        return results

    def listOutcomesKPI(self):
        items = api.content.find(
            portal_type=['OutcomeKPI', 'OutcomeZONE'],
            context=self.context)
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        data_year = self.context.gwopa_year_phases[int(self.year) - 1]
        for item in items:
            members = []
            obj = item.getObject()
            annotations = IAnnotations(obj)
            if KEY in annotations.keys():
                if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
                    target_value_real = ''
                    target_value_planned = _(u"Not defined")
                    monitoring_info = ''
                else:
                    target_value_real = annotations[KEY]['real']
                    target_value_planned = annotations[KEY]['planned']
                    monitoring_info = annotations[KEY]['monitoring']
            else:
                target_value_real = ''
                target_value_planned = '-----'
            if obj.members:
                users = obj.members
                for member in users:
                    members.append(api.user.get(username=member).getProperty('fullname'))
            results.append(dict(
                path=item.getPath(),
                id=item.id,
                year=self.year,
                portal_type=item.portal_type,
                start=item.start,
                title=item.Title,
                description=item.Description,
                base_value=obj.baseline,
                base_date=obj.baseline_date.strftime('%Y-%m'),
                zone=obj.zone,
                unit=obj.measuring_unit,
                means=obj.means,
                risks=obj.risks,
                responsible=members,
                next_update=data_year['end_iso'][0:7],
                target_value_real=target_value_real,
                target_value_planned=target_value_planned,
                consideration=monitoring_info['consideration'] if monitoring_info is not '' else '',
                explanation=monitoring_info['explanation'] if monitoring_info is not '' else '',
                obstacles=monitoring_info['obstacles'] if monitoring_info is not '' else '',
                contributing=monitoring_info['contributing'] if monitoring_info is not '' else '',
                limiting=monitoring_info['limiting'] if monitoring_info is not '' else '',
                progress=monitoring_info['progress'] if monitoring_info is not '' else '',
                updated=monitoring_info['updated'] if monitoring_info is not '' else '',
                url='/'.join(obj.getPhysicalPath())))
        return results

    def listOutcomesCC(self):
        items = api.content.find(
            portal_type=['OutcomeCC'],
            context=self.context)
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in items:
            members = []
            obj = item.getObject()
            annotations = IAnnotations(item.getObject())
            base_value = ''
            base_date = ''
            description = ''
            objective = ''
            objective_date = ''
            target_value_planned = _(u"Not defined")
            specifics = ''
            monitoring = ''
            if KEY in annotations.keys():
                if annotations[KEY] != '' or annotations[KEY] is not None or annotations[KEY] != 'None':
                    base_value = annotations[KEY]['generic'][0]['baseline']
                    base_date = annotations[KEY]['generic'][0]['baseline_date']
                    description = annotations[KEY]['generic'][0]['description']
                    objective = annotations[KEY]['generic'][0]['objective']
                    objective_date = annotations[KEY]['generic'][0]['objective_date']
                    target_value_planned = annotations[KEY]['planned']
                    specifics = annotations[KEY]['specifics']
                    monitoring = annotations[KEY]['monitoring']

            if obj.members:
                users = obj.members
                if isinstance(users, (str,)):
                    members.append(api.user.get(username=users[0]).getProperty('fullname'))
                else:
                    for member in users:
                        members.append(api.user.get(username=member).getProperty('fullname'))
            if obj.aq_parent.portal_type == 'ImprovementArea':
                area = obj.aq_parent.title
            else:
                area = obj.aq_parent.aq_parent.title
            results.append(dict(
                rid=item.getRID(),
                area=area,
                title=item.Title,
                description=description,
                base_date=base_date,
                base_value=base_value,
                objective=objective,
                objective_date=objective_date,
                target_value_planned=target_value_planned,
                specifics=specifics,
                monitoring=monitoring,
                portal_type=item.portal_type,
                responsible=members,
                url='/'.join(obj.getPhysicalPath())))

        return results

    def custom_pattern_options(self):
        """ Pass data from project to picker date in modal, in Activity, OutcomeKPI and OutcomeKPIZone.
            Output must be done via JS because we need to pass the value from the HTML. """
        start = self.context.gwopa_year_phases[:][0]['pattern_start']
        end = self.context.gwopa_year_phases[-1:][0]['pattern_end']
        value = """{"date":{ "min":[""" + start + """], "max":[""" + \
            end + """]}, "time": false, "today": false, "clear": false}"""
        return value
