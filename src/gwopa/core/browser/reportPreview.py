# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from decimal import Decimal
from operator import itemgetter
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from gwopa.core import _
from gwopa.core import utils
from gwopa.core.utils import getTitleAttrLang
from gwopa.core.utils import getUserLang

import datetime


@implementer(IPublishTraverse)
class reportPreviewView(BrowserView):
    """ Shows all the reporting options associated to one project
    """
    index = ViewPageTemplateFile('templates/reportPreview.pt')

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(reportPreviewView, self).__init__(context, request)
        self.year = None
        path_ordered = request.path[-1:]
        # get all param in the path -> the year /planning/2019
        self.year = '/'.join(path_ordered)

    def __call__(self):
        if self.request['URL'].split('/')[-1][0:4] == 'api-':
            self.request.response.redirect(self.request['URL'].replace('reportPreview/', ''))

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

    def getPhases(self):
        return len(self.context.gwopa_year_phases)

    def getItems(self):
        """ Returns all the project years of the planning """
        items = len(self.context.gwopa_year_phases)
        results = []
        total = 0

        while total != items:
            if (total == 0) and (self.request.steps[-1] == 'reportPreview'):
                classe = 'disabled'
            elif self.request.steps[-1] == str(total + 1):
                classe = 'disabled'
            else:
                classe = 'visible'
            if total == 0:
                url = self.context.absolute_url_path() + '/reportPreview/'
            else:
                url = self.context.absolute_url_path() + '/reportPreview/' + str(total + 1)
            results.append(dict(
                title=_(u"Project year"),
                year=str(total + 1),
                url=url,
                alt=_(u"Show report preview of year ") + str(total + 1),
                classe=classe))
            total = total + 1

        return sorted(results, key=itemgetter('title'), reverse=False)

    def getYear(self):
        return self.year

    def getFaseStart(self):
        return self.fase_start

    def getFaseEnd(self):
        return self.fase_end

    def projectTitle(self):
        return self.context.title

    def projectURL(self):
        return self.context.absolute_url()

    def getProjectWaterOperators(self):
        result = []
        waterOperators = api.content.find(
            portal_type=['ContribPartner'],
            path='/'.join(self.context.getPhysicalPath()) + '/contribs/',
            depth=2
        )

        for wo in waterOperators:
            wo = wo.getObject()
            result.append({
                'name': wo.title,
                'role': "",  # TODO Mentee / Mentor
                'incash': str(0 if wo.incash is None else wo.incash),
                'inkind': str(0 if wo.inkind is None else wo.inkind)
            })

        return result

    def getProjectDonors(self):
        result = []
        waterOperators = api.content.find(
            portal_type=['ContribDonor'],
            path='/'.join(self.context.getPhysicalPath()) + '/contribs/',
            depth=2
        )

        for wo in waterOperators:
            wo = wo.getObject()
            result.append({
                'name': wo.title,
                'incash': str(0 if wo.incash is None else wo.incash),
                'inkind': str(0 if wo.inkind is None else wo.inkind)
            })

        return result

    def getProjectOtherOrganizations(self):
        result = []
        waterOperators = api.content.find(
            portal_type=['ContribOther'],
            path='/'.join(self.context.getPhysicalPath()) + '/contribs/',
            depth=2
        )

        for wo in waterOperators:
            wo = wo.getObject()
            result.append({
                'name': wo.title,
                'role': "",  # TODO Broker / Technical Support / Political Support / Other
                'incash': str(0 if wo.incash is None else wo.incash),
                'inkind': str(0 if wo.inkind is None else wo.inkind)
            })

        return result

    def getTotalBudget(self, contribs):
        total = 0
        for contrib in contribs:
            total += Decimal(contrib['incash']) + Decimal(contrib['inkind'])

        return str(total)

    def getTotalAssignedBudget(self, activities):
        total = 0
        for activity in activities:
            try:
                total += Decimal(activity['assigned_budget'])
            except:
                pass

        return str(total)

    def getWorkingAreas(self):
        return api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context)

    def getActivitiesWA(self, wa):
        return api.content.find(
            portal_type=['Activity'],
            context=wa)

    def getOutputsActivity(self, activity):
        return api.content.find(
            portal_type=['Output'],
            context=activity)

    def getOutcomes(self):
        return api.content.find(
            portal_type=['OutcomeZONE'],
            context=self.context)

    def getOutcomesCapacityWA(self, wa):
        return api.content.find(
            portal_type=['OutcomeCC'],
            context=wa)

    def getTitleSpecific(self, specific):
        lang = getUserLang()
        if lang in ['es', 'fr']:
            return specific['title_specific_' + lang]
        else:
            return specific['title_specific']

    def getStyles(self):
        return {
            'style1': "border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000;",
            'style2': "border-top: 2px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000; border-right: 1px solid #000000;",
            'style3': "border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-right: 1px solid #000000;",
            'style4': "border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000;",
            'style5': "border-top: 2px solid #000000; border-bottom: 1px solid #000000; border-left: 1px solid #000000;"
        }

    def reportData(self):
        data = {}
        attr_lang = getTitleAttrLang()

        today = datetime.datetime.now()
        data['generation_report_date'] = today.strftime('%m/%d/%Y %H:%M:%S')

        data['project_overview'] = {
            'project_name': self.context.title,
            'project_code': "",  # empty
            'reporting_type': utils.getTranslatedMesuringFrequencyFromID(self.context.measuring_frequency),
            'reporting_period': {
                'from': "",  # TODO ???
                'to': ""  # TODO ????
            },
            'author_report': "Project Manager (Administrator) " + "",  # TODO ???
            'position_report': "Project Manager (Administrator) " + "",  # TODO ???
            'currency': utils.project_currency(self),
            'water_operators': self.getProjectWaterOperators(),  # Array
            'donors': self.getProjectDonors(),  # Array
            'other_organizations': self.getProjectOtherOrganizations(),  # Array
            'total_budget': "",
            'project_location': {
                'country': self.context.country,
                'location': self.context.location
            },
            'project_duration': {
                'start': self.context.startactual.strftime('%m/%d/%Y'),
                'end': self.context.completionactual.strftime('%m/%d/%Y')
            },
            'association': {
                'wop_platform': self.context.wop_platform,
                'wop_program': self.context.wop_program
            },
            'project_description': self.context.objectives,
        }

        data['project_overview']['total_budget'] = self.getTotalBudget(
            data['project_overview']['water_operators'] +
            data['project_overview']['donors'] +
            data['project_overview']['other_organizations'])

        working_areas = self.getWorkingAreas()
        data['summary'] = {
            'working_areas': ", ".join([getattr(wa, attr_lang) for wa in working_areas]),
            'progress': "",  # empty
            'other': ""  # empty
        }

        data['activities_outputs'] = {}
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)

        for wa in working_areas:
            wa_title = getattr(wa, attr_lang)
            data['activities_outputs'].update({wa_title: {
                'title': wa_title,
                'activities': {},
            }})

            activities = self.getActivitiesWA(wa.getObject())
            for activity in activities:
                activityObj = activity.getObject()
                activityAnn = IAnnotations(activityObj)
                activity_title = activityObj.title
                data['activities_outputs'][wa_title]['activities'].update({activity_title: {
                    'title': activity_title,
                    'start': activityObj.start.strftime('%m/%d/%Y'),
                    'completion': activityObj.end.strftime('%m/%d/%Y'),
                    'progress_tracker': {
                        'progress': activityAnn[KEY]['monitoring']['progress'] if 'progress' in activityAnn[KEY]['monitoring'] else "",
                        'real': '100',
                        'measuring_unit': '%',
                    },
                    'description': {
                        'description': activityObj.description,
                        'planning': activityObj.initial_situation,
                        'explanation_progress': activityAnn[KEY]['monitoring']['explanation'] if 'explanation' in activityAnn[KEY]['monitoring'] else "",
                    },
                    'main_obstacles': {
                        'internal': "X" if 'obstacles' in activityAnn[KEY]['monitoring'] and 'Internal organizational' in activityAnn[KEY]['monitoring']['obstacles'] else "",
                        'external': "X" if 'obstacles' in activityAnn[KEY]['monitoring'] and 'External environment' in activityAnn[KEY]['monitoring']['obstacles'] else "",
                        "wop_related": "X" if 'obstacles' in activityAnn[KEY]['monitoring'] and 'WOP project - related' in activityAnn[KEY]['monitoring']['obstacles'] else "",
                    },
                    'main_contributing': {
                        'internal': "X" if 'contributing' in activityAnn[KEY]['monitoring'] and 'Internal organizational' in activityAnn[KEY]['monitoring']['contributing'] else "",
                        'external': "X" if 'contributing' in activityAnn[KEY]['monitoring'] and 'External environment' in activityAnn[KEY]['monitoring']['contributing'] else "",
                        "wop_related": "X" if 'contributing' in activityAnn[KEY]['monitoring'] and 'WOP project - related' in activityAnn[KEY]['monitoring']['contributing'] else "",
                    },
                    'explain_limiting': activityAnn[KEY]['monitoring']['limiting'] if 'limiting' in activityAnn[KEY]['monitoring'] else "",
                    'cosidetation_for_future': activityAnn[KEY]['monitoring']['consideration'] if 'consideration' in activityAnn[KEY]['monitoring'] else "",
                    'means_of_verification': "",  # TODO ???
                    'outputs': {}
                }})

                outputs = self.getOutputsActivity(activityObj)
                for output in outputs:
                    outputObj = output.getObject()
                    outputAnn = IAnnotations(outputObj)
                    output_title = outputObj.title
                    data['activities_outputs'][wa_title]['activities'][activity_title]['outputs'].update({output_title: {
                        'title': output_title,
                        'start': outputObj.start.strftime('%m/%d/%Y'),
                        'completion': outputObj.end.strftime('%m/%d/%Y'),
                        'progress_tracker': {
                            'progress': outputAnn[KEY]['monitoring']['explanation'] if 'explanation' in outputAnn[KEY]['monitoring'] else "",
                            'real': outputAnn[KEY]['real'],
                            'measuring_unit': utils.getTranslatedMesuringUnitFromID(outputObj.measuring_unit),
                        },
                        'description': {
                            'description': outputObj.description,
                            'explanation_progress': outputAnn[KEY]['monitoring']['explanation'] if 'explanation' in outputAnn[KEY]['monitoring'] else "",
                        },
                        'main_obstacles': {
                            'internal': "X" if 'obstacles' in outputAnn[KEY]['monitoring'] and 'Internal organizational' in outputAnn[KEY]['monitoring']['obstacles'] else "",
                            'external': "X" if 'obstacles' in outputAnn[KEY]['monitoring'] and 'External environment' in outputAnn[KEY]['monitoring']['obstacles'] else "",
                            "wop_related": "X" if 'obstacles' in outputAnn[KEY]['monitoring'] and 'WOP project - related' in outputAnn[KEY]['monitoring']['obstacles'] else "",
                        },
                        'main_contributing': {
                            'internal': "X" if 'contributing' in outputAnn[KEY]['monitoring'] and 'Internal organizational' in outputAnn[KEY]['monitoring']['contributing'] else "",
                            'external': "X" if 'contributing' in outputAnn[KEY]['monitoring'] and 'External environment' in outputAnn[KEY]['monitoring']['contributing'] else "",
                            "wop_related": "X" if 'contributing' in outputAnn[KEY]['monitoring'] and 'WOP project - related' in outputAnn[KEY]['monitoring']['contributing'] else "",
                        },
                        'explain_limiting': outputAnn[KEY]['monitoring']['limiting'] if 'limiting' in outputAnn[KEY]['monitoring'] else "",
                        'cosidetation_for_future': outputAnn[KEY]['monitoring']['consideration'] if 'consideration' in outputAnn[KEY]['monitoring'] else "",
                        'means_of_verification': "",  # TODO ???
                    }})


        data['outcomes'] = {}
        outcomes = self.getOutcomes()
        for outcome in outcomes:
            outcomeObj = outcome.getObject()
            annotations = IAnnotations(outcomeObj)
            outcome_title = getattr(outcome, attr_lang)
            data['outcomes'].update({outcome_title : {
                'title': outcome_title,
                'zone': outcomeObj.zone,
                'baseline_date': outcomeObj.baseline_date.strftime('%Y-%m'),
                'baseline_value': outcomeObj.baseline,
                'target_value_real': annotations[KEY]['real'],
                'target_value_planned': annotations[KEY]['planned'],
                'description': {
                    'description': outcomeObj.description,
                    'explanation_progress': annotations[KEY]['monitoring']['explanation'] if 'explanation' in annotations[KEY]['monitoring'] else "",
                },
                'main_obstacles': {
                    'internal': "X" if 'obstacles' in annotations[KEY]['monitoring'] and 'Internal organizational' in annotations[KEY]['monitoring']['obstacles'] else "",
                    'external': "X" if 'obstacles' in annotations[KEY]['monitoring'] and 'External environment' in annotations[KEY]['monitoring']['obstacles'] else "",
                    "wop_related": "X" if 'obstacles' in annotations[KEY]['monitoring'] and 'WOP project - related' in annotations[KEY]['monitoring']['obstacles'] else "",
                },
                'main_contributing': {
                    'internal': "X" if 'contributing' in annotations[KEY]['monitoring'] and 'Internal organizational' in annotations[KEY]['monitoring']['contributing'] else "",
                    'external': "X" if 'contributing' in annotations[KEY]['monitoring'] and 'External environment' in annotations[KEY]['monitoring']['contributing'] else "",
                    "wop_related": "X" if 'contributing' in annotations[KEY]['monitoring'] and 'WOP project - related' in annotations[KEY]['monitoring']['contributing'] else "",
                },
                'explain_contributed': annotations[KEY]['monitoring']['limiting'] if 'limiting' in annotations[KEY]['monitoring'] else "",
                'consideration': annotations[KEY]['monitoring']['consideration'] if 'consideration' in annotations[KEY]['monitoring'] else "",
                'means_of_verification': outcomeObj.means,  # TODO ???
            }})

        data['outcomes_capacity'] = {}
        for wa in working_areas:
            wa_title = getattr(wa, attr_lang)
            data['outcomes_capacity'].update({wa_title: {
                'title': wa_title,
                'capacities': {},
            }})

            outcomecc = self.getOutcomesCapacityWA(wa.getObject())[0]
            annotations = IAnnotations(outcomecc.getObject())
            for capacity in annotations[KEY]['monitoring']:
                if 'selected' in capacity['selected_specific']:
                    capacity_title = self.getTitleSpecific(capacity)
                    data['outcomes_capacity'][wa_title]['capacities'].update({capacity_title: {
                        'title': capacity_title,
                        'consensus': capacity['consensus'],
                        'main_obstacles': {
                            'internal': "X" if 'obstacles' in capacity and 'Internal organizational' in capacity['obstacles'] else "",
                            'external': "X" if 'obstacles' in capacity and 'External environment' in capacity['obstacles'] else "",
                            "wop_related": "X" if 'obstacles' in capacity and 'WOP project - related' in capacity['obstacles'] else "",
                        },
                        'main_contributing': {
                            'internal': "X" if 'contributing_factors' in capacity and 'Internal organizational' in capacity['contributing_factors'] else "",
                            'external': "X" if 'contributing_factors' in capacity and 'External environment' in capacity['contributing_factors'] else "",
                            "wop_related": "X" if 'contributing_factors' in capacity and 'WOP project - related' in capacity['contributing_factors'] else "",
                        },
                        'explain': capacity['explain'],
                        'means_of_verification': "",  # TODO ???
                    }})


        data['budget'] = {
            'planned_activities': [],
            'total_budget': "",
        }

        allActivities = api.content.find(
            portal_type=['Activity'],
            context=self.context)

        for activity in allActivities:
            activityObj = activity.getObject()
            data['budget']['planned_activities'].append({
                'wa_title': getattr(activityObj.aq_parent, attr_lang.lower()),
                'title': activity.Title,
                'assigned_budget': activityObj.budget,
            })

        data['budget']['total_budget'] = self.getTotalAssignedBudget(data['budget']['planned_activities'])
        return data
