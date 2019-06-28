# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone import api
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from operator import itemgetter
from gwopa.core import _
from zope.annotation.interfaces import IAnnotations


@implementer(IPublishTraverse)
class dashboardAreasView(BrowserView):
    """ Dashboard Areas View """

    index = ViewPageTemplateFile("templates/dash-areas.pt")

    def publishTraverse(self, request, name):
        # Stop traversing, we have arrived
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        """Once we get to __call__, the path is lost so we
           capture it here on initialization
        """
        super(dashboardAreasView, self).__init__(context, request)
        self.year = None
        path_ordered = request.path[-1:]
        # get all param in the path -> the year /dash-areas/2019
        self.year = '/'.join(path_ordered)

    def getYear(self):
        return self.year

    def projectTitle(self):
        return self.context.title

    def __call__(self):
        if self.request['URL'].split('/')[-1][0:4] == 'api-':
            self.request.response.redirect(self.request['URL'].replace('dash-areas/', ''))
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

    def getItems(self):
        """ Returns all the project years of the dash-areas """
        items = len(self.context.gwopa_year_phases)
        results = []
        total = 0

        while total != items:
            if (total == 0) and (self.request.steps[-1] == 'dash-areas'):
                classe = 'disabled'
            elif self.request.steps[-1] == str(total + 1):
                classe = 'disabled'
            else:
                classe = 'visible'
            if total == 0:
                url = self.context.absolute_url_path() + '/dash-areas/'
            else:
                url = self.context.absolute_url_path() + '/dash-areas/' + str(total + 1)
            results.append(dict(
                title=_(u"Project year"),
                year=str(total + 1),
                url=url,
                alt=_(u"Show dashboard of year ") + str(total + 1),
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

    def getOutcomeCC(self):
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

    def getCurrentStage(self):
        """ Returns all the stages for each Improvement Areas in a Project """
        items = api.content.find(
            portal_type=['OutcomeCC'],
            context=self.context)
        results = []
        KEY = "GWOPA_TARGET_YEAR_" + str(self.year)
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
