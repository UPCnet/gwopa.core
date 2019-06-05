# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from Products.CMFCore.utils import getToolByName
import datetime
from gwopa.core import _
from zope.annotation.interfaces import IAnnotations


@implementer(IPublishTraverse)
class planningView(BrowserView):
    """ Planning View """

    index = ViewPageTemplateFile("templates/planning.pt")

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(planningView, self).__init__(context, request)
        self.year = None
        path_ordered = request.path[-1:]
        # get all param in the path -> the year /planning/2019
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
        currency = self.context.currency
        return currency.split('-')[-1:][0] if currency is not None else ''

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
            self.request.response.redirect(self.request['URL'].replace('planning/', ''))
        if (not self.year or self.year == '0'):
            # Empty query or 0 returns default template (First Year)
            self.year = 1
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
        """ Returns all the project years of the planning """
        items = len(self.context.gwopa_year_phases)
        results = []
        total = 0

        while total != items:
            if (total == 0) and (self.request.steps[-1] == 'planning'):
                classe = 'disabled'
            elif self.request.steps[-1] == str(total + 1):
                classe = 'disabled'
            else:
                classe = 'visible'
            if total == 0:
                url = self.context.absolute_url_path() + '/planning/'
            else:
                url = self.context.absolute_url_path() + '/planning/' + str(total + 1)
            results.append(dict(
                title=_(u"Project year"),
                year=str(total + 1),
                url=url,
                alt=_(u"Show planning of year "),
                classe=classe))
            total = total + 1
        return sorted(results, key=itemgetter('title'), reverse=False)

    def getAreas(self):
        """ Returns all the Improvement Areas in a Project """
        items = api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context)
        results = []
        for (i, project) in enumerate(items):
            item = project.getObject()
            results.append(dict(title=item.title,
                                url='/'.join(item.getPhysicalPath()),
                                id=item.id,
                                description=item.description,
                                pos=i,
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
            members = []
            obj = item.getObject()
            annotations = IAnnotations(item.getObject())
            if KEY in annotations.keys():
                if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
                    target_value_planned = _(u"Not defined")
                    unit = ''
                else:
                    target_value_planned = annotations[KEY]['planned']
            else:
                target_value_planned = _(u"Not defined")
            if item.portal_type == 'Activity':
                unit = ''
            else:
                unit = obj.measuring_unit
            if not item.start:
                item.start = '-----'
            if not item.end:
                item.end = '-----'
            if obj.members:
                users = obj.members
                if isinstance(users, (str,)):
                    members.append(api.user.get(username=users).getProperty('fullname'))
                else:
                    for member in users:
                        members.append(api.user.get(username=member).getProperty('fullname'))
            if item.portal_type == 'Activity':
                unit = ''
                target_value_planned = '-----'
            if item.portal_type == 'Output':
                start = '----'
                limit_start = '----'
            else:
                start = item.start.strftime('%Y-%m')
                limit_start = item.start.strftime('%Y %m %d').replace(' 0', ' ').replace(' ', ',')
            results.append(dict(
                title=item.Title,
                description=item.Description,
                portal_type=item.portal_type,
                start=start,
                end=item.end.strftime('%Y-%m'),
                unit=unit,
                limit_start=limit_start,
                limit_end=item.end.strftime('%Y %m %d').replace(' 0', ' ').replace(' ', ','),
                target_value_planned=target_value_planned,
                responsible=members,
                url='/'.join(obj.getPhysicalPath())))
        return results

    def listOutcomesKPI(self):
        items = api.content.find(
            portal_type=['OutcomeKPI', 'OutcomeZONE'],
            context=self.context)
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in items:
            members = []
            obj = item.getObject()
            annotations = IAnnotations(item.getObject())
            if KEY in annotations.keys():
                if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
                    target_value_planned = _(u"Not defined")
                    unit = ''
                else:
                    target_value_planned = annotations[KEY]['planned']
                    unit = obj.measuring_unit
            else:
                target_value_planned = _(u"Not defined")
                unit = ''
            if obj.members:
                users = obj.members
                if isinstance(users, (str,)):
                    members.append(api.user.get(username=users[0]).getProperty('fullname'))
                else:
                    for member in users:
                        members.append(api.user.get(username=member).getProperty('fullname'))
            results.append(dict(
                title=item.Title,
                description=item.Description,
                base_date=obj.baseline_date.strftime('%Y-%m'),
                base_value=obj.baseline,
                zone=obj.zone,
                unit=unit,
                target_value_planned=target_value_planned,
                measuring_unit=obj.measuring_unit,
                measuring_frequency=obj.measuring_frequency,
                portal_type=item.portal_type,
                responsible=members,
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
            target_value_planned = ''
            specifics = ''
            if KEY in annotations.keys():
                if annotations[KEY] != '' or annotations[KEY] is not None or annotations[KEY] != 'None':
                    base_value = annotations[KEY]['generic'][0]['baseline']
                    base_date = annotations[KEY]['generic'][0]['baseline_date']
                    description = annotations[KEY]['generic'][0]['description']
                    objective = annotations[KEY]['generic'][0]['objective']
                    objective_date = annotations[KEY]['generic'][0]['objective_date']
                    target_value_planned = annotations[KEY]['planned']
                    specifics = annotations[KEY]['specifics']

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
                portal_type=item.portal_type,
                responsible=members,
                url='/'.join(obj.getPhysicalPath())))

        return results

    # def listOutcomesCCS(self):
    #     items = api.content.find(
    #         portal_type=['OutcomeCCS'],
    #         context=self.context)
    #     results = []
    #     KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
    #     for item in items:
    #         members = []
    #         obj = item.getObject()
    #         annotations = IAnnotations(item.getObject())
    #         if KEY in annotations.keys():
    #             if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
    #                 target_value_planned = _(u"Not defined")
    #                 unit = ''
    #             else:
    #                 target_value_planned = annotations[KEY]['planned']
    #                 unit = obj.measuring_unit
    #         else:
    #             target_value_planned = _(u"Not defined")
    #             unit = ''
    #         if obj.members:
    #             users = obj.members
    #             if isinstance(users, (str,)):
    #                 members.append(api.user.get(username=users[0]).getProperty('fullname'))
    #             else:
    #                 for member in users:
    #                     members.append(api.user.get(username=member).getProperty('fullname'))
    #         if obj.aq_parent.portal_type == 'ImprovementArea':
    #             area = obj.aq_parent.title
    #         else:
    #             area = obj.aq_parent.aq_parent.title
    #         results.append(dict(
    #             id=item.id,
    #             area=area,
    #             title=item.Title,
    #             # description=item.Description,
    #             # base_date=obj.baseline_date.strftime('%Y-%m'),
    #             # base_value=obj.baseline,
    #             # zone=obj.zone,
    #             # unit=unit,
    #             # target_value_planned=target_value_planned,
    #             # measuring_unit=obj.measuring_unit,
    #             # measuring_frequency=obj.measuring_frequency,
    #             # portal_type=item.portal_type,
    #             # responsible=members,
    #             url='/'.join(obj.getPhysicalPath())))
    #
    #     return results

    def custom_pattern_options(self):
        """ Pass data from project to picker date in modal, in Activity, OutcomeKPI and OutcomeKPIZone.
            Output must be done via JS because we need to pass the value from the HTML. """
        start = self.context.gwopa_year_phases[:][0]['pattern_start']
        end = self.context.gwopa_year_phases[-1:][0]['pattern_end']
        value = """{"date":{ "min":[""" + start + """], "max":[""" + \
            end + """]}, "time": false, "today": false, "clear": false}"""
        return value
