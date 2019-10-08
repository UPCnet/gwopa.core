# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from operator import itemgetter
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from gwopa.core import _
from gwopa.core.utils import getTitleAttrLang
from gwopa.core.utils import getTranslatedMesuringUnitFromID
from gwopa.core.utils import getTranslatedOutcomesFromTitle
from gwopa.core.utils import getUserLang
from gwopa.core.utils import project_currency

import datetime


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
        return project_currency(self)

    def getPath(self):
        return '/'.join(self.context.getPhysicalPath())

    def project_start(self):
        start = self.context.startactual.strftime('%Y-%m-%d')
        return start

    def project_end(self):
        end = self.context.completionactual.strftime('%Y-%m-%d')
        return end

    def project_frequency(self):
        return self.context.measuring_frequency  # TODO Actualmente no se utiliza, revisar si hace falta traducir

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
                alt=_(u"Show planning of year ") + str(total + 1),
                classe=classe))
            total = total + 1

        return sorted(results, key=itemgetter('title'), reverse=False)

    def getAreas(self):
        """ Returns all the Improvement Areas in a Project """
        attr_lang = getTitleAttrLang()
        items = api.content.find(
            portal_type=['ImprovementArea'],
            context=self.context)
        results = []
        for (i, project) in enumerate(items):
            item = project.getObject()
            results.append(dict(title=getattr(project, attr_lang),
                                url='/'.join(item.getPhysicalPath()),
                                id=item.id,
                                description=item.Description(),
                                pos=i,
                                portal_type=item.portal_type
                                ))

        return sorted(results, key=itemgetter('title'), reverse=False)

    def activitiesInside(self, item):
        """ Returns Activities inside Working Area """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        data_year = self.context.gwopa_year_phases[int(self.year) - 1]
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

        elements = []

        for item in items:
            if item.getObject() not in elements:
                elements.append(item.getObject())
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in elements:
            members = []
            annotations = IAnnotations(item)
            target_value_planned = _(u"Not defined")
            if KEY in annotations.keys():
                if annotations[KEY] != '' or annotations[KEY] is not None or annotations[KEY] != 'None':
                    target_value_planned = annotations[KEY]['planned']

            if item.members:
                users = item.members
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

            results.append(dict(
                title=item.title,
                portal_type=item.portal_type,
                start=item.start.strftime('%Y-%m-%d'),
                end=item.end.strftime('%Y-%m-%d'),
                limit_start=item.start.strftime('%Y %m %d').replace(' 0', ' ').replace(' ', ','),
                limit_end=item.end.strftime('%Y %m %d').replace(' 0', ' ').replace(' ', ','),
                target_value_planned='-----',
                responsible=members,
                url='/'.join(item.getPhysicalPath())))

        return sorted(results, key=itemgetter('title'), reverse=False)

    def outputsInside(self, item):
        """  Returns Outpus inside Activities """
        portal_catalog = getToolByName(self, 'portal_catalog')
        folder_path = item['url']
        data_year = self.context.gwopa_year_phases[int(self.year) - 1]

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

        elements = []
        for item in items:
            if item.getObject() not in elements:
                elements.append(item.getObject())
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in elements:
            members = []
            members_id = []
            annotations = IAnnotations(item)
            target_value_planned = _(u"Not defined")
            if KEY in annotations.keys():
                if annotations[KEY] != '' or annotations[KEY] is not None or annotations[KEY] != 'None':
                    target_value_planned = annotations[KEY]['planned']

            if item.members:
                users = item.members
                if isinstance(users, (str,)):
                    for member in users.split(','):
                        user = api.user.get(username=member)
                        if user:
                            members.append(user.getProperty('fullname'))
                            members_id.append(member)
                else:
                    for member in users:
                        user = api.user.get(username=member)
                        if user:
                            members.append(user.getProperty('fullname'))
                            members_id.append(member)

            if item.description:
                description = item.description
            else:
                description = ''

            if item.means:
                means = item.means
            else:
                means = ''

            # if item.risks:
            #     risks = item.risks
            # else:
            #     risks = ''

            results.append(dict(
                title=item.title,
                portal_type=item.portal_type,
                start='----',
                end=item.end.strftime('%Y-%m-%d'),
                unit=item.measuring_unit,
                unit_text=getTranslatedMesuringUnitFromID(item.measuring_unit),
                limit_start='----',
                limit_end=item.end.strftime('%Y %m %d').replace(' 0', ' ').replace(' ', ','),
                target_value_planned=target_value_planned,
                responsible=members,
                responsible_id=members_id,
                description=description,
                means=means,
                # risks=risks,
                url='/'.join(item.getPhysicalPath())))

        return sorted(results, key=itemgetter('title'), reverse=False)

    def listOutcomesKPI(self):
        items = api.content.find(
            portal_type=['OutcomeZONE'],
            context=self.context)
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
        for item in items:
            members = []
            members_id = []
            obj = item.getObject()
            annotations = IAnnotations(item.getObject())
            if KEY in annotations.keys():
                if annotations[KEY] == '' or annotations[KEY] is None or annotations[KEY] == 'None':
                    target_value_planned = _(u"Not defined")
                    unit = ''
                else:
                    target_value_planned = annotations[KEY]['planned']
                    unit = getTranslatedMesuringUnitFromID(obj.measuring_unit)
            else:
                target_value_planned = _(u"Not defined")
                unit = ''

            if obj.members:
                users = obj.members
                if isinstance(users, (str,)):
                    for member in users.split(','):
                        user = api.user.get(username=member)
                        if user:
                            members.append(user.getProperty('fullname'))
                            members_id.append(member)
                else:
                    for member in users:
                        user = api.user.get(username=member)
                        if user:
                            members.append(user.getProperty('fullname'))
                            members_id.append(member)

            if obj.means:
                means = obj.means
            else:
                means = ''

            # if obj.risks:
            #     risks = obj.risks
            # else:
            #     risks = ''
            results.append(dict(
                title=getTranslatedOutcomesFromTitle(item.Title),
                description=item.Description,
                base_date=obj.baseline_date.strftime('%Y-%m'),
                base_date_edit=obj.baseline_date.strftime('%Y-%m-%d'),
                base_value=obj.baseline,
                zone=obj.zone,
                unit=unit,
                unit_text=getTranslatedMesuringUnitFromID(obj.measuring_unit),
                target_value_planned=target_value_planned,
                portal_type=item.portal_type,
                responsible=members,
                responsible_id=members_id,
                means=means,
                # risks=risks,
                url='/'.join(obj.getPhysicalPath())))

        return sorted(results, key=itemgetter('title'), reverse=False)

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
                    for member in users.split(','):
                        user = api.user.get(username=member)
                        if user:
                            members.append(user.getProperty('fullname'))
                else:
                    for member in users:
                        user = api.user.get(username=member)
                        if user:
                            members.append(user.getProperty('fullname'))

            attr_lang = getTitleAttrLang()
            if obj.aq_parent.portal_type == 'ImprovementArea':
                area = getattr(obj.aq_parent, attr_lang)
            else:
                area = getattr(obj.aq_parent.aq_parent, attr_lang)
            results.append(dict(
                rid=item.getRID(),
                area=area,
                title=item.title,
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

        return sorted(results, key=itemgetter('title'), reverse=False)

    def custom_pattern_options(self):
        """ Pass data from project to picker date in modal, in Activity and OutcomeKPIZone.
            Output must be done via JS because we need to pass the value from the HTML. """
        start = self.context.gwopa_year_phases[:][0]['pattern_start']
        end = self.context.gwopa_year_phases[-1:][0]['pattern_end']
        value = """{"date":{ "min":[""" + start + """], "max":[""" + \
            end + """]}, "time": false, "today": false, "clear": false}"""
        return value

    def getTitleSpecific(self, specific):
        lang = getUserLang()
        if lang in ['es', 'fr']:
            return specific['title_specific_' + lang]
        else:
            return specific['title_specific']
