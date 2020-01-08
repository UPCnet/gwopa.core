# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from plone.namedfile import field as namedfile
from plone import api
from gwopa.core import _
from gwopa.core import utils
from gwopa.core.utils import getTitleAttrLang
from gwopa.core.utils import getUserLang
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from decimal import Decimal
from operator import itemgetter
from zope.annotation.interfaces import IAnnotations
import datetime
from plone.app.textfield import RichText

grok.templatedir("templates")


def listSectionsReport(context):
    sections = []
    sections.append(SimpleVocabulary.createTerm(u'Project Overview', 'Project Overview', _(u'Project Overview')))
    sections.append(SimpleVocabulary.createTerm(u'Summary', 'Summary', _(u'Summary')))
    sections.append(SimpleVocabulary.createTerm(u'Activities and Outputs Progress', 'Activities and Outputs Progress', _(u'Activities and Outputs Progress')))
    sections.append(SimpleVocabulary.createTerm(u'Outcomes', 'Outcomes', _(u'Outcomes')))
    sections.append(SimpleVocabulary.createTerm(u'Budget', 'Budget', _(u'Budget')))
    return SimpleVocabulary(sections)


directlyProvides(listSectionsReport, IContextSourceBinder)


def getProjectYears(self):
        """ Returns all the project years of the project """
        items = len(self.__parent__.gwopa_year_phases)
        project_years = []
        total = 0

        while total != items:
            project_years.append(SimpleVocabulary.createTerm(str(total + 1), str(total + 1), (str(total + 1))))
            total = total + 1

        return SimpleVocabulary(project_years)


directlyProvides(getProjectYears, IContextSourceBinder)


def getOverallStatus(self):
    status = []
    status.append(SimpleVocabulary.createTerm(u'roadblock', 'roadblock', _(u'Roadblock')))
    status.append(SimpleVocabulary.createTerm(u'potential', 'potential', _(u'Potential Risks/Delays')))
    status.append(SimpleVocabulary.createTerm(u'ontrack', 'ontrack', _(u'On Track')))
    return SimpleVocabulary(status)


directlyProvides(getOverallStatus, IContextSourceBinder)


class IReport(model.Schema):
    """  Report type
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    project_code = schema.TextLine(
        title=_(u'Project Code'),
        required=False,
        missing_value=u'',
    )

    overall_project_status = schema.Choice(
        title=_(u"Overall Project Status"),
        description=_(u"Select the overall Project status."),
        source=getOverallStatus,
        required=True,
    )

    progress_stakeholders = RichText(
        title=_(u'Progress stakeholders'),
        description=_(u"Insert a maximum of two paragraphs summarizing the progress during the reporting period that could be shared with the programs key stakeholders."),
        required=False,
        missing_value=u'',
    )

    other_additional_challenges = RichText(
        title=_(u'Other additional challenges'),
        description=_(u"Insert a maximum of two paragraphs summarizig the or other additional challenges/ lessons learned/ deviations to plans."),
        required=False,
        missing_value=u'',
    )

    image_logo = namedfile.NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )

    project_year = schema.Choice(
        title=_(u"Project Year"),
        description=_(u"Choose project year to view in the report."),
        source=getProjectYears,
        required=True,
    )

    sections_reports = schema.List(
        title=_(u"Sections Report"),
        description=_(u"Choose sections to view in the report."),
        value_type=schema.Choice(
            source=listSectionsReport),
        required=True,
    )


class View(grok.View):
    grok.context(IReport)
    grok.template('report_view')
    grok.require('zope2.View')

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
        return int(self.context.project_year)

    def getFaseStart(self):
        return self.context.gwopa_year_phases[int(self.context.project_year) - 1]['start']

    def getFaseEnd(self):
        return self.context.gwopa_year_phases[int(self.context.project_year) - 1]['end']

    def projectTitle(self):
        return self.context.title

    def projectURL(self):
        return self.context.__parent__.__parent__.absolute_url()

    def getProjectManagerAdmin(self):
        result = []
        user = api.user.get(self.context.project_manager_admin)
        result.append(dict(
            id=user.id,
            fullname=user.getProperty('fullname'),
            position=user.getProperty('position')))

        return result

    def getProjectWaterOperators(self, project):
        result = []
        waterOperators = api.content.find(
            portal_type=['ContribPartner'],
            path='/'.join(project.getPhysicalPath()) + '/contribs/',
            depth=2
        )

        for wo in waterOperators:
            wo = wo.getObject()
            result.append({
                'name': wo.title,
                'role': wo.partner_roles,
                'incash': str(0 if wo.incash is None else wo.incash),
                'inkind': str(0 if wo.inkind is None else wo.inkind)
            })

        return result

    def getProjectDonors(self, project):
        result = []
        waterOperators = api.content.find(
            portal_type=['ContribDonor'],
            path='/'.join(project.getPhysicalPath()) + '/contribs/',
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

    def getProjectOtherOrganizations(self, project):
        result = []
        waterOperators = api.content.find(
            portal_type=['ContribOther'],
            path='/'.join(project.getPhysicalPath()) + '/contribs/',
            depth=2
        )

        for wo in waterOperators:
            wo = wo.getObject()
            result.append({
                'name': wo.title,
                'role': wo.organization_roles,
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

    def getWorkingAreas(self, project):
        return api.content.find(
            portal_type=['ImprovementArea'],
            context=project)

    def getActivitiesWA(self, wa):
        """ returns objects from first level (elements inside ImprovementArea) """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(wa.getPhysicalPath())
        data_year = self.context.gwopa_year_phases[int(self.getYear()) - 1]
        start = datetime.datetime.strptime(data_year['start_iso'], '%Y-%m-%d')
        end = datetime.datetime.strptime(data_year['end_iso'], '%Y-%m-%d')

        # Los de la fase [---]
        range_start = {'query': (start, end), 'range': 'min:max'}
        range_end = {'query': (start, end), 'range': 'min:max'}
        activities1 = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            start=range_start,
            end=range_end,
            path={'query': folder_path,
                  'depth': 1})

        # Los de fuera de la fase start y end ---][----
        range_start = {'query': (start), 'range': 'max'}
        range_end = {'query': (end), 'range': 'min'}
        activities2 = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            start=range_start,
            end=range_end,
            path={'query': folder_path,
                  'depth': 1})

        # Los que empiezan antes y acaban en fase ---]
        ranges = {'query': (start), 'range': 'max'}
        range_end = {'query': (start, end), 'range': 'min:max'}

        activities3 = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            start=ranges,
            end=range_end,
            path={'query': folder_path,
                  'depth': 1})

        # Los que empiezan aqui y acaban despues [----
        range_start = {'query': (start, end), 'range': 'min:max'}
        range_end = {'query': (end), 'range': 'min'}
        activities4 = portal_catalog.unrestrictedSearchResults(
            portal_type=['Activity'],
            start=range_start,
            end=range_end,
            path={'query': folder_path,
                  'depth': 1})

        items = activities1 + activities2 + activities3 + activities4

        return items

    def getOutputsActivity(self, activity):
        """ Returns Outpus inside Activities  """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = '/'.join(activity.getPhysicalPath())
        data_year = self.context.gwopa_year_phases[int(self.getYear()) - 1]
        start = datetime.datetime.strptime(data_year['start_iso'], '%Y-%m-%d')
        end = datetime.datetime.strptime(data_year['end_iso'], '%Y-%m-%d')

        range_end = {'query': (start, end), 'range': 'min:max'}
        outputs1 = portal_catalog.unrestrictedSearchResults(
            portal_type=['Output'],
            end=range_end,
            path={'query': folder_path,
                  'depth': 1})

        range_end = {'query': (end), 'range': 'min'}
        outputs2 = portal_catalog.unrestrictedSearchResults(
            portal_type=['Output'],
            end=range_end,
            path={'query': folder_path,
                  'depth': 1})

        items = outputs1 + outputs2

        return items

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

    def viewProjectOverview(self):
        return 'Project Overview' in self.context.sections_reports

    def viewSummary(self):
        return 'Summary' in self.context.sections_reports

    def viewActivities(self):
        return 'Activities and Outputs Progress' in self.context.sections_reports

    def viewOutcomes(self):
        return 'Outcomes' in self.context.sections_reports

    def viewBudget(self):
        return 'Budget' in self.context.sections_reports

    def reportData(self):
        data = {}
        attr_lang = getTitleAttrLang()
        project_manager_admin = self.getProjectManagerAdmin()
        today = datetime.datetime.now()

        project = self.context.aq_parent.aq_parent

        data['generation_report_date'] = today.strftime('%m/%d/%Y %H:%M:%S')
        data['project_overview'] = {
            'project_name': project.title,
            'project_code': self.context.project_code,
            'reporting_type': utils.getTranslatedMesuringFrequencyFromID(project.measuring_frequency),
            'reporting_period': {
                'project_year': self.getYear(),
                'from': self.getFaseStart(),
                'to': self.getFaseEnd()
            },
            'author_report': project_manager_admin[0]['fullname'],
            'position_report': project_manager_admin[0]['position'],
            'currency': utils.project_currency(self),
            'water_operators': self.getProjectWaterOperators(project),  # Array
            'donors': self.getProjectDonors(project),  # Array
            'other_organizations': self.getProjectOtherOrganizations(project),  # Array
            'total_budget': "",
            'project_location': {
                'country': project.country,
                'location': project.location
            },
            'project_duration': {
                'start': project.startactual.strftime('%m/%d/%Y'),
                'end': project.completionactual.strftime('%m/%d/%Y')
            },
            'association': {
                'wop_platform': project.wop_platform,
                'wop_program': project.wop_program
            },
            'project_description': project.objectives,
        }

        data['project_overview']['total_budget'] = self.getTotalBudget(
            data['project_overview']['water_operators'] +
            data['project_overview']['donors'] +
            data['project_overview']['other_organizations'])

        working_areas = self.getWorkingAreas(project)
        data['summary'] = {
            'working_areas': ", ".join([getattr(wa, attr_lang) for wa in working_areas]),
            'progress': {
                'roadblock': self.context.overall_project_status == 'roadblock',
                'potential': self.context.overall_project_status == 'potential',
                'ontrack': self.context.overall_project_status == 'ontrack',
                'stakeholders': self.context.progress_stakeholders,
            },
            'other': self.context.other_additional_challenges,
        }

        data['activities_outputs'] = {}
        KEY = "GWOPA_TARGET_YEAR_" + str(self.getYear())

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
                            'progress': outputAnn[KEY]['planned'],
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
            data['outcomes'].update({outcome_title: {
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
            context=project)

        for activity in allActivities:
            activityObj = activity.getObject()
            data['budget']['planned_activities'].append({
                'wa_title': getattr(activityObj.aq_parent, attr_lang.lower()),
                'title': activity.Title,
                'assigned_budget': activityObj.budget,
            })

        data['budget']['total_budget'] = self.getTotalAssignedBudget(data['budget']['planned_activities'])
        return data