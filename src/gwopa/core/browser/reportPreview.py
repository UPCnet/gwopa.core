# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

import datetime
from decimal import Decimal
from plone import api
from zope.annotation.interfaces import IAnnotations

from gwopa.core import utils
from gwopa.core.utils import getTitleAttrLang


class reportPreviewView(BrowserView):
    """ Shows all the reporting options associated to one project
    """
    __call__ = ViewPageTemplateFile('templates/reportPreview.pt')

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

    def getWorkingAreas(self):
        return api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context)

    def getActivitiesWA(self, wa):
        return api.content.find(
            portal_type=['Activity'],
            context=wa)

    def reportData(self):
        data = {}
        attr_lang = getTitleAttrLang()

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
            'project_description': self.context.objectives
        }

        today = datetime.date.today()

        data['generation_report_date'] = today.strftime('%m/%d/%Y')

        data.update({'total_budget': self.getTotalBudget(
            data['project_overview']['water_operators'] +
            data['project_overview']['donors'] +
            data['project_overview']['other_organizations'])})

        working_areas = self.getWorkingAreas()
        data['summary'] = {
            'working_areas': ", ".join([getattr(wa, attr_lang) for wa in working_areas]),
            'progress': "",  # empty
            'other': ""  # empty
        }

        data['activities_outputs'] = {}
        KEY = "GWOPA_TARGET_YEAR_1" #TODO

        for wa in working_areas:
            data['activities_outputs'].update({
                'title': getattr(wa, attr_lang),
                'activities': [],
            })

            activities = self.getActivitiesWA(wa)
            for activity in activities:
                activityObj = activity.getObject()
                annotations = IAnnotations(activityObj)
                data['activities_outputs']['activities'].append({
                    'title': getattr(activity, attr_lang),
                    'start': activityObj.start.strftime('%m/%d/%Y'),
                    'completion': activityObj.end.strftime('%m/%d/%Y'),
                    'progress_tracker': annotations[KEY]['monitoring']['progress'] if 'progress' in annotations[KEY]['monitoring'] else "",
                    'description': {
                        'description': activityObj.description,
                        'planning': activityObj.initial_situation,
                        'explanation_progress': annotations[KEY]['monitoring']['explanation'] if 'explanation' in annotations[KEY]['monitoring'] else "",
                    },
                    'main_obstacles': {
                        'internal': "X" if 'obstacles' in annotations[KEY]['monitoring'] and 'Internal organizational' in annotations[KEY]['monitoring']['obstacles'] else "",
                        'external': "X" if 'obstacles' in annotations[KEY]['monitoring'] and 'External environment' in
                            annotations[KEY]['monitoring']['obstacles'] else "",
                        "wop_related": "X" if 'obstacles' in annotations[KEY]['monitoring'] and 'WOP project - related' in annotations[KEY]['monitoring']['obstacles'] else "",
                    },
                    'main_contributing': {
                        'internal': "X" if 'contributing' in annotations[KEY]['monitoring'] and 'Internal organizational' in annotations[KEY]['monitoring']['contributing'] else "",  # TODO "X" if 'Internal organizational' in annotations[KEY]['monitoring']['contributing_factors'] else "",
                        'external': "X" if 'contributing' in annotations[KEY]['monitoring'] and 'External environment' in annotations[KEY]['monitoring']['contributing'] else "",  # TODO "X" if 'External environment' in annotations[KEY]['monitoring']['contributing_factors'] else "",
                        "wop_related": "X" if 'contributing' in annotations[KEY]['monitoring'] and 'WOP project - related' in annotations[KEY]['monitoring']['contributing'] else "",  # TODO "X" if 'WOP project - related' in annotations[KEY]['monitoring']['contributing_factors'] else "",
                    },
                    'explain_contributed': annotations[KEY]['monitoring']['contributing'] if 'contributing' in annotations[KEY]['monitoring'] else "",
                    'cosidetation_for_future': annotations[KEY]['monitoring']['consideration'] if 'consideration' in annotations[KEY]['monitoring'] else "",
                    'means_of_verification': "",  # TODO ???
                    'outputs': []
                })

        data['outcomes'] = {

        }

        data['budget'] = {

        }

        return data
