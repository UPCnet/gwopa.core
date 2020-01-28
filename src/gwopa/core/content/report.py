# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName

from decimal import Decimal
from five import grok
from operator import itemgetter
from plone import api
from plone.autoform import directives as form
from plone.schema.jsonfield import JSONField
from plone.supermodel import model
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import directlyProvides
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary

from gwopa.core import _
from gwopa.core import utils
from gwopa.core.utils import getTitleAttrLang
from gwopa.core.utils import getTranslatedOutcomesFromTitle
from gwopa.core.utils import getUserLang

import datetime
import random
import transaction

grok.templatedir("templates")


def listSectionsReport(context):
    sections = []
    sections.append(SimpleVocabulary.createTerm(u'Project Overview', 'Project Overview', _(u'Project Overview')))
    sections.append(SimpleVocabulary.createTerm(u'Summary', 'Summary', _(u'Summary')))
    sections.append(SimpleVocabulary.createTerm(u'Activities and Outputs Progress', 'Activities and Outputs Progress', _(u'Activities and Outputs Progress')))
    sections.append(SimpleVocabulary.createTerm(u'Outcomes - Utility Perfomance', 'Outcomes - Utility Perfomance', _(u'Outcomes - Utility Perfomance')))
    sections.append(SimpleVocabulary.createTerm(u'Outcomes - Capacity', 'Outcomes - Capacity', _(u'Outcomes - Capacity')))
    sections.append(SimpleVocabulary.createTerm(u'Budget', 'Budget', _(u'Budget')))
    sections.append(SimpleVocabulary.createTerm(u'Next Steps', 'Next Steps', _(u'Next Steps')))
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


def getReportTypes(self):
    status = []
    status.append(SimpleVocabulary.createTerm(u'manual', 'manual', _(u'Manual')))
    status.append(SimpleVocabulary.createTerm(u'auto', 'auto', _(u'Auto')))
    return SimpleVocabulary(status)


directlyProvides(getReportTypes, IContextSourceBinder)


class IReport(model.Schema):
    """  Report type
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    form.mode(overall_project_status='hidden')
    overall_project_status = schema.Choice(
        title=_(u"Overall Project Status"),
        description=_(u"Select the overall Project status."),
        source=getOverallStatus,
        required=False,
    )

    form.mode(progress_stakeholders='hidden')
    progress_stakeholders = schema.Text(
        title=_(u'Progress stakeholders'),
        description=_(u"Insert a maximum of two paragraphs summarizing the progress during the reporting period that could be shared with the programs key stakeholders."),
        required=False,
        missing_value=u'',
    )

    form.mode(other_additional_challenges='hidden')
    other_additional_challenges = schema.Text(
        title=_(u'Other additional challenges'),
        description=_(u"Insert a maximum of two paragraphs summarizig the or other additional challenges/ lessons learned/ deviations to plans."),
        required=False,
        missing_value=u'',
    )

    form.mode(next_steps='hidden')
    next_steps = schema.Text(
        title=_(u'Next Steps'),
        required=False,
        missing_value=u'',
    )

    form.mode(IEditForm, project_year='hidden')
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
        default=['Project Overview', 'Summary', 'Activities and Outputs Progress', 'Outcomes - Utility Perfomance', 'Outcomes - Capacity', 'Next Steps', 'Budget'],
        required=True,
    )

    form.mode(save_data='hidden')
    save_data = JSONField(
        title=_(u"Data"),
        required=False,
    )

    form.mode(report_type='hidden')
    report_type = schema.Choice(
        title=_(u"Type"),
        source=getReportTypes,
        default=u'manual',
        required=False,
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
        if self.context.project_manager_admin:
            user = api.user.get(self.context.project_manager_admin)
            if user:
                result.append(dict(
                    id=user.id,
                    fullname=user.getProperty('fullname'),
                    position=user.getProperty('position')))
                return result

        result.append(dict(
            id='',
            fullname='',
            position=''))
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
                total += Decimal(activities[activity]['assigned_budget'])
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

    def getOutcomes(self, project):
        return api.content.find(
            portal_type=['OutcomeZONE'],
            context=project)

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

    def viewOutcomesUtilityPerfomance(self):
        return 'Outcomes - Utility Perfomance' in self.context.sections_reports

    def viewOutcomesCapacity(self):
        return 'Outcomes - Capacity' in self.context.sections_reports

    def viewBudget(self):
        return 'Budget' in self.context.sections_reports

    def viewNextSteps(self):
        return 'Next Steps' in self.context.sections_reports

    def getLogosFirstpage(self, project):
        """ Returns all the KPIs from project  """

        logos = []

        # DONORS
        if project.donors:
            for donor in project.donors:
                items = api.content.find(
                    portal_type=['Donor'],
                    Title=donor)

                if items and items[0].getObject().image:
                    logos.append({'name': donor,
                                  'url': items[0].getURL() + '/@@images/image'})

        # PLATFOWMS OR PROGRAMS
        if project.wop_platform:
            items = api.content.find(
                portal_type=['Platform'],
                Title=project.wop_platform)

            if items and items[0].getObject().image:
                logos.append({'name': project.wop_platform,
                              'url': items[0].getURL() + '/@@images/image'})

        if project.wop_program:
            items = api.content.find(
                portal_type=['Program'],
                Title=project.wop_program)

            if items and items[0].getObject().image:
                logos.append({'name': project.wop_program,
                              'url': items[0].getURL() + '/@@images/image'})

        # WATER OPERATORS
        if project.partners:
            for partner in project.partners:
                items = api.content.find(
                    portal_type=['Partner'],
                    Title=partner)

                if items and items[0].getObject().image:
                    logos.append({'name': partner,
                                  'url': items[0].getURL() + '/@@images/image'})

        return logos

    def getHexColor(self, pos):
        if pos < 10:
            colors = ['#007bb1', '#f49200', '#cce4ef', '#fce9cc', '#001823', '#301d00', '#00496a', '#925700', '#66afd0', '#f8bd66']
            return colors[pos]
        else:
            random_number = random.randint(0, 16777215)
            hex_number = str(hex(random_number))
            return '#' + hex_number[2:]

    def reportData(self):

        project = self.context.aq_parent.aq_parent
        if self.context.save_data and self.context.save_data != "":
            self.context.save_data['project_overview']['project_name'] = project.title
            self.context.save_data['project_overview']['project_code'] = project.code
            self.context.save_data['summary']['progress']['roadblock'] = self.context.overall_project_status == 'roadblock'
            self.context.save_data['summary']['progress']['potential'] = self.context.overall_project_status == 'potential'
            self.context.save_data['summary']['progress']['ontrack'] = self.context.overall_project_status == 'ontrack'
            self.context.save_data['summary']['progress']['stakeholders'] = self.context.progress_stakeholders
            self.context.save_data['summary']['other'] = self.context.other_additional_challenges
            self.context.save_data['next_steps'] = self.context.next_steps
            return self.context.save_data

        data = {}
        attr_lang = getTitleAttrLang()
        project_manager_admin = self.getProjectManagerAdmin()
        today = datetime.datetime.now()
        data['project_url'] = project.absolute_url()
        data['generation_report_date'] = today.strftime('%m/%d/%Y %H:%M:%S')
        data['project_overview'] = {
            'project_name': project.title,
            'project_code': project.code,
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
            'project_description': project.objectives.output if hasattr(project.objectives, 'output') else '',
            'project_image': project.absolute_url() + '/@@images/image' if project.image else None,
            'logos': self.getLogosFirstpage(project),
        }

        data['project_overview']['total_budget'] = self.getTotalBudget(
            data['project_overview']['water_operators'] +
            data['project_overview']['donors'] +
            data['project_overview']['other_organizations'])

        totalBugdets = int(data['project_overview']['total_budget'])
        dataChartBudgets = {'chart': {'water_operators': {'series': [],
                                                          'colors': []},
                                      'donors': {'series': [],
                                                 'colors': []},
                                      'other_organizations': {'series': [],
                                                              'colors': []}},
                            'legend': {'water_operators': [],
                                       'donors': [],
                                       'other_organizations': []}}

        pos = totalWO = 0
        for wo in data['project_overview']['water_operators']:
            inkind = int(wo['inkind']) if 'inkind' in wo and wo['inkind'] else 0
            incash = int(wo['incash']) if 'incash' in wo and wo['incash'] else 0
            woValue = inkind + incash
            totalWO += woValue

            dataChartBudgets['chart']['water_operators']['series'].append(woValue)

            color = self.getHexColor(pos)
            pos += 1
            dataChartBudgets['chart']['water_operators']['colors'].append(color)

            wo.update({'color': color})
            dataChartBudgets['legend']['water_operators'].append(wo)

        dataChartBudgets['chart']['water_operators']['series'].append(totalBugdets - totalWO)
        dataChartBudgets['chart']['water_operators']['colors'].append('#F1F1F1')

        dataChartBudgets['chart']['donors']['series'].append(totalWO)
        dataChartBudgets['chart']['donors']['colors'].append('#F1F1F1')

        pos = totalDonors = 0
        for donor in data['project_overview']['donors']:
            inkind = int(donor['inkind']) if 'inkind' in donor and donor['inkind'] else 0
            incash = int(donor['incash']) if 'incash' in donor and donor['incash'] else 0
            donorsValue = inkind + incash
            totalDonors += donorsValue

            dataChartBudgets['chart']['donors']['series'].append(donorsValue)

            color = self.getHexColor(pos)
            pos += 1
            dataChartBudgets['chart']['donors']['colors'].append(color)

            donor.update({'color': color})
            dataChartBudgets['legend']['donors'].append(donor)

        dataChartBudgets['chart']['donors']['series'].append(totalBugdets - totalWO - totalDonors)
        dataChartBudgets['chart']['donors']['colors'].append('#F1F1F1')

        dataChartBudgets['chart']['other_organizations']['series'].append(totalWO + totalDonors)
        dataChartBudgets['chart']['other_organizations']['colors'].append('#F1F1F1')

        pos = totalOO = 0
        for oo in data['project_overview']['other_organizations']:
            inkind = int(oo['inkind']) if 'inkind' in oo and oo['inkind'] else 0
            incash = int(oo['incash']) if 'incash' in oo and oo['incash'] else 0
            ooValue = inkind + incash
            totalOO += ooValue

            dataChartBudgets['chart']['other_organizations']['series'].append(ooValue)

            color = self.getHexColor(pos)
            pos += 1
            dataChartBudgets['chart']['other_organizations']['colors'].append(color)

            oo.update({'color': color})
            dataChartBudgets['legend']['other_organizations'].append(oo)

        data['project_overview'].update({'chart_budget': dataChartBudgets['chart'],
                                         'chart_budget_legend': dataChartBudgets['legend']})

        working_areas = self.getWorkingAreas(project)
        data['summary'] = {
            'working_areas': ", ".join([getattr(wa, attr_lang) for wa in working_areas]),
            'progress': {
                'roadblock': self.context.overall_project_status == 'roadblock',
                'potential': self.context.overall_project_status == 'potential',
                'ontrack': self.context.overall_project_status == 'ontrack',
                'stakeholders': self.context.progress_stakeholders
            },
            'other': self.context.other_additional_challenges
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
                        'progress': activityAnn[KEY]['monitoring']['progress'] if 'progress' in activityAnn[KEY]['monitoring'] and activityAnn[KEY]['monitoring']['progress'] else 0,
                        'real': '100',
                        'measuring_unit': '%',
                        'style': ''
                    },
                    'description': {
                        'description': activityObj.description,
                        'planning': activityObj.initial_situation,
                        'explanation_progress': activityAnn[KEY]['monitoring']['explanation'] if 'explanation' in activityAnn[KEY]['monitoring'] else "",
                    },
                    'main_obstacles': {
                        'internal': 'obstacles' in activityAnn[KEY]['monitoring'] and 'Internal organizational' in activityAnn[KEY]['monitoring']['obstacles'],
                        'external': 'obstacles' in activityAnn[KEY]['monitoring'] and 'External environment' in activityAnn[KEY]['monitoring']['obstacles'],
                        "wop_related": 'obstacles' in activityAnn[KEY]['monitoring'] and 'WOP project - related' in activityAnn[KEY]['monitoring']['obstacles'],
                    },
                    'main_contributing': {
                        'internal': 'contributing' in activityAnn[KEY]['monitoring'] and 'Internal organizational' in activityAnn[KEY]['monitoring']['contributing'],
                        'external': 'contributing' in activityAnn[KEY]['monitoring'] and 'External environment' in activityAnn[KEY]['monitoring']['contributing'],
                        "wop_related": 'contributing' in activityAnn[KEY]['monitoring'] and 'WOP project - related' in activityAnn[KEY]['monitoring']['contributing'],
                    },
                    'explain_limiting': activityAnn[KEY]['monitoring']['limiting'] if 'limiting' in activityAnn[KEY]['monitoring'] else "",
                    'cosidetation_for_future': activityAnn[KEY]['monitoring']['consideration'] if 'consideration' in activityAnn[KEY]['monitoring'] else "",
                    'outputs': {}
                }})

                progress = int(data['activities_outputs'][wa_title]['activities'][activity_title]['progress_tracker']['progress'])
                data['activities_outputs'][wa_title]['activities'][activity_title]['progress_tracker']['style'] = 'transform: translateX(' + str(progress - 100) + '%);'

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
                            'progress': outputAnn[KEY]['planned'] if 'planned' in outputAnn[KEY] and outputAnn[KEY]['planned'] else 0,
                            'real': outputAnn[KEY]['real'] if 'real' in outputAnn[KEY] and outputAnn[KEY]['real'] else 0,
                            'measuring_unit': utils.getTranslatedMesuringUnitFromID(outputObj.measuring_unit),
                            'style': ''
                        },
                        'description': {
                            'description': outputObj.description,
                            'explanation_progress': outputAnn[KEY]['monitoring']['explanation'] if 'explanation' in outputAnn[KEY]['monitoring'] else "",
                        },
                        'main_obstacles': {
                            'internal': 'obstacles' in outputAnn[KEY]['monitoring'] and 'Internal organizational' in outputAnn[KEY]['monitoring']['obstacles'],
                            'external': 'obstacles' in outputAnn[KEY]['monitoring'] and 'External environment' in outputAnn[KEY]['monitoring']['obstacles'],
                            "wop_related": 'obstacles' in outputAnn[KEY]['monitoring'] and 'WOP project - related' in outputAnn[KEY]['monitoring']['obstacles'],
                        },
                        'main_contributing': {
                            'internal': 'contributing' in outputAnn[KEY]['monitoring'] and 'Internal organizational' in outputAnn[KEY]['monitoring']['contributing'],
                            'external': 'contributing' in outputAnn[KEY]['monitoring'] and 'External environment' in outputAnn[KEY]['monitoring']['contributing'],
                            "wop_related": 'contributing' in outputAnn[KEY]['monitoring'] and 'WOP project - related' in outputAnn[KEY]['monitoring']['contributing'],
                        },
                        'explain_limiting': outputAnn[KEY]['monitoring']['limiting'] if 'limiting' in outputAnn[KEY]['monitoring'] else "",
                        'cosidetation_for_future': outputAnn[KEY]['monitoring']['consideration'] if 'consideration' in outputAnn[KEY]['monitoring'] else "",
                        'means_of_verification': outputObj.means,
                    }})

                    try:
                        progress = int(float(data['activities_outputs'][wa_title]['activities'][activity_title]['outputs'][output_title]['progress_tracker']['real']) / float(data['activities_outputs'][wa_title]['activities'][activity_title]['outputs'][output_title]['progress_tracker']['progress']) * 100)
                    except:
                        progress = 0

                    data['activities_outputs'][wa_title]['activities'][activity_title]['outputs'][output_title]['progress_tracker']['style'] = 'transform: translateX(' + str(progress - 100) + '%);'

        data['outcomes'] = {'dash_info': getItems(project),
                            'list': {}}

        outcomes = self.getOutcomes(project)
        for outcome in outcomes:
            outcomeObj = outcome.getObject()
            annotations = IAnnotations(outcomeObj)
            outcome_title = getattr(outcome, attr_lang)
            data['outcomes']['list'].update({outcome_title: {
                'title': outcome_title,
                'zone': outcomeObj.zone,
                'baseline_date': outcomeObj.baseline_date.strftime('%Y-%m'),
                'baseline_value': outcomeObj.baseline,
                'target_value_real': annotations[KEY]['real'] if 'real' in annotations[KEY] and annotations[KEY]['real'] else 0,
                'target_value_planned': annotations[KEY]['planned'] if 'planned' in annotations[KEY] and annotations[KEY]['planned'] else 0,
                'target_value_style': '',
                'description': {
                    'description': outcomeObj.description,
                    'explanation_progress': annotations[KEY]['monitoring']['explanation'] if 'explanation' in annotations[KEY]['monitoring'] else "",
                },
                'main_obstacles': {
                    'internal': 'obstacles' in annotations[KEY]['monitoring'] and 'Internal organizational' in annotations[KEY]['monitoring']['obstacles'],
                    'external': 'obstacles' in annotations[KEY]['monitoring'] and 'External environment' in annotations[KEY]['monitoring']['obstacles'],
                    "wop_related": 'obstacles' in annotations[KEY]['monitoring'] and 'WOP project - related' in annotations[KEY]['monitoring']['obstacles'],
                },
                'main_contributing': {
                    'internal': 'contributing' in annotations[KEY]['monitoring'] and 'Internal organizational' in annotations[KEY]['monitoring']['contributing'],
                    'external': 'contributing' in annotations[KEY]['monitoring'] and 'External environment' in annotations[KEY]['monitoring']['contributing'],
                    "wop_related": 'contributing' in annotations[KEY]['monitoring'] and 'WOP project - related' in annotations[KEY]['monitoring']['contributing'],
                },
                'explain_contributed': annotations[KEY]['monitoring']['limiting'] if 'limiting' in annotations[KEY]['monitoring'] else "",
                'consideration': annotations[KEY]['monitoring']['consideration'] if 'consideration' in annotations[KEY]['monitoring'] else "",
                'means_of_verification': outcomeObj.means,  # TODO ???
            }})

            try:
                progress = int(float(data['outcomes']['list'][outcome_title]['target_value_real']) / float(data['outcomes']['list'][outcome_title]['target_value_planned']) * 100)
            except:
                progress = 0

            data['outcomes']['list'][outcome_title]['target_value_style'] = 'transform: translateX(' + str(progress - 100) + '%);'

        data['outcomes_capacity'] = {}
        for wa in working_areas:
            wa_title = getattr(wa, attr_lang)
            wa_object = wa.getObject()
            data['outcomes_capacity'].update({wa_title: {
                'title': wa_title,
                'getCurrentStage': getCurrentStage(wa_object, self.getYear()),
                'getOutcomeCC': getOutcomeCC(wa_object, self.getYear()),
                'capacities': {},
            }})

            outcomecc = self.getOutcomesCapacityWA(wa_object)[0]
            annotations = IAnnotations(outcomecc.getObject())
            for capacity in annotations[KEY]['monitoring']:
                if 'selected' in capacity['selected_specific']:
                    capacity_title = self.getTitleSpecific(capacity)
                    data['outcomes_capacity'][wa_title]['capacities'].update({capacity_title: {
                        'title': capacity_title,
                        'degree_changes': capacity['degree_changes'] if 'degree_changes' in capacity and capacity['degree_changes'] else '',
                        'contributed_project': capacity['contributed_project'] if 'contributed_project' in capacity and capacity['contributed_project'] else '',
                        'consensus': capacity['consensus'] if 'consensus' in capacity and capacity['consensus'] else '',
                        'main_obstacles': {
                            'internal': 'obstacles' in capacity and 'Internal organizational' in capacity['obstacles'],
                            'external': 'obstacles' in capacity and 'External environment' in capacity['obstacles'],
                            "wop_related": 'obstacles' in capacity and 'WOP project - related' in capacity['obstacles'],
                        },
                        'main_contributing': {
                            'internal': 'contributing_factors' in capacity and 'Internal organizational' in capacity['contributing_factors'],
                            'external': 'contributing_factors' in capacity and 'External environment' in capacity['contributing_factors'],
                            "wop_related": 'contributing_factors' in capacity and 'WOP project - related' in capacity['contributing_factors'],
                        },
                        'explain': capacity['explain'],
                        'means_of_verification': "",  # TODO ???
                    }})

        data['budget'] = {
            'planned_activities': {},
            'total_budget': "",
        }

        allActivities = api.content.find(
            portal_type=['Activity'],
            context=project)

        for activity in allActivities:
            act_title = '[' + getattr(activityObj.aq_parent, attr_lang.lower()) + '] ' + activity.Title
            activityObj = activity.getObject()
            data['budget']['planned_activities'].update({act_title: {
                'title': act_title,
                'assigned_budget': activityObj.budget,
                'expenditure_reporting_period': '',
                'total_expenditure_date': '',
            }})

        data['budget']['total_budget'] = self.getTotalAssignedBudget(data['budget']['planned_activities'])

        data['next_steps'] = self.context.next_steps

        self.context.save_data = data
        return data


def getOutcomeCC(wa, year):
    items = api.content.find(
        portal_type=['OutcomeCC'],
        context=wa)
    results = []
    KEY = "GWOPA_TARGET_YEAR_" + str(year)
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
                for member in users.split(','):
                    user = api.user.get(username=member)
                    if user:
                        members.append(user.getProperty('fullname'))
            else:
                for member in users:
                    user = api.user.get(username=member)
                    if user:
                        members.append(user.getProperty('fullname'))

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
    if len(results) != 0:
        return results[0]
    else:
        return False


def getCurrentStage(wa, year):
    """ Returns all the stages for each Improvement Areas in a Project """
    items = api.content.find(
        portal_type=['OutcomeCC'],
        context=wa)
    results = []
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

    return results[0:4]


def getItems(project):
    """ Returns all the KPIs from project  """
    items = api.content.find(
        portal_type=['OutcomeZONE'],
        context=project)

    results = []
    if len(items) != 0:
        for (i, project) in enumerate(items):
            item = project.getObject()

            results.append(dict(title=getTranslatedOutcomesFromTitle(item.title),
                                url='/'.join(item.getPhysicalPath()),
                                id=item.id,
                                pos=i,
                                ))
        return sorted(results, key=itemgetter('title'), reverse=False)
    else:
        return None


class ModifySummaryStatus(grok.View):
    grok.context(IReport)
    grok.require('zope2.View')

    def render(self):
        self.context.overall_project_status = self.request.form.get('status')
        self.context.reindexObject()
        transaction.commit()


class ModifySummaryProgressStakeholders(grok.View):
    grok.context(IReport)
    grok.require('zope2.View')

    def render(self):
        self.context.progress_stakeholders = self.request.form.get('text')
        self.context.reindexObject()
        transaction.commit()


class ModifySummaryOtherAdditionalChallenges(grok.View):
    grok.context(IReport)
    grok.require('zope2.View')

    def render(self):
        self.context.other_additional_challenges = self.request.form.get('text')
        self.context.reindexObject()
        transaction.commit()


class ModifyExpenditureReportingPeriod(grok.View):
    grok.context(IReport)
    grok.require('zope2.View')

    def render(self):
        activity = self.request.form.get('activity', '')
        self.context.save_data['budget']['planned_activities'][activity]['expenditure_reporting_period'] = self.request.form.get('text', '')
        self.context.reindexObject()
        transaction.commit()


class ModifyTotalExpenditureDate(grok.View):
    grok.context(IReport)
    grok.require('zope2.View')

    def render(self):
        activity = self.request.form.get('activity', '')
        self.context.save_data['budget']['planned_activities'][activity]['total_expenditure_date'] = self.request.form.get('text', '')
        self.context.reindexObject()
        transaction.commit()


class ModifyNextSteps(grok.View):
    grok.context(IReport)
    grok.require('zope2.View')

    def render(self):
        self.context.next_steps = self.request.form.get('text')
        self.context.reindexObject()
        transaction.commit()
