from zope.interface import implements
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.interfaces import IMainTemplate
from plone import api
from bs4 import BeautifulSoup
from operator import itemgetter
import random


class MainTemplate(BrowserView):
    implements(IMainTemplate)

    main_template = ViewPageTemplateFile('templates/homepage.pt')

    def __call__(self):
        return self.template()

    @property
    def template(self):
        return self.main_template

    @property
    def macros(self):
        return self.template.macros

    def isManager(self):
        currentuser = api.user.get_current().id
        roles_currentuser = api.user.get_roles(username=currentuser)
        if 'Manager' in roles_currentuser or 'Site Administrator' in roles_currentuser:
            return True
        else:
            return False

    def canAdd(self):
        # Can create projects
        currentuser = api.user.get_current().id
        roles = ['Manager', 'Site Administrator', 'Contributor']
        for role in roles:
            if role in api.user.get_roles(username=currentuser):
                return True
        return False

    def myProjects(self):
        catalog = api.portal.get_tool('portal_catalog')
        currentuser = api.user.get_current().id
        results = []
        limit = 4
        roles_currentuser = api.user.get_roles(username=currentuser)
        if 'Manager' in roles_currentuser or 'Site Administrator' in roles_currentuser:
            projects = catalog.unrestrictedSearchResults(
                portal_type='Project',
                context=self.context,
                sort_order='reverse',
                sort_on='modified',
                sort_limit=limit)
            for project in projects:
                item = project._unrestrictedGetObject()
                if item.image:
                    image = item.absolute_url() + '/@@images/image/preview'
                else:
                    image = item.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
                if item.objectives:
                    alt = self.abreviaText(item.objectives.raw, 400)
                else:
                    alt = self.abreviaText(item.title)
                results.append(dict(title=self.abreviaText(item.title),
                                    alt=alt,
                                    url=item.absolute_url(),
                                    start=item.startplanned,
                                    end=item.startactual,
                                    country=item.country,
                                    location=item.location,
                                    project_manager=item.project_manager,
                                    image=image
                                    ))
        else:           
            projects = catalog.unrestrictedSearchResults(
                portal_type='Project',
                context=self.context,
                sort_order='reverse',
                sort_on='modified')
            for project in projects:
                members_project = []
                item = project._unrestrictedGetObject()
                if item.members:
                    for i in item.members:
                        members_project.append(i)
                if item.project_manager:
                    for i in item.project_manager:
                        members_project.append(i)
                if item.project_manager_admin:
                    members_project.append(item.project_manager_admin)             
                if members_project:
                    if currentuser in members_project:
                        if item.image:
                            image = item.absolute_url() + '/@@images/image/preview'
                        else:
                            image = item.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
                        if item.objectives:
                            alt = self.abreviaText(item.objectives.raw, 400)
                        else:
                            alt = self.abreviaText(item.title)
                        results.append(dict(title=self.abreviaText(item.title),
                                            alt=alt,
                                            url=item.absolute_url(),
                                            start=item.startplanned,
                                            end=item.startactual,
                                            country=item.country,
                                            location=item.location,
                                            project_manager=item.project_manager,
                                            image=image
                                            ))
        return sorted(results, key=itemgetter('title'), reverse=False)

    def companyProjects(self):
        catalog = api.portal.get_tool('portal_catalog')
        results = []
        # Manager views all projects
        currentuser = api.user.get_current().id
        roles_currentuser = api.user.get_roles(username=currentuser)
        if 'Manager' in roles_currentuser or 'Site Administrator' in roles_currentuser:
            projects = catalog.unrestrictedSearchResults(
                portal_type='Project',
                context=self.context)
            for project in projects:
                item = project._unrestrictedGetObject()
                if item.image:
                    image = item.absolute_url() + '/@@images/image/preview'
                else:
                    image = item.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
                if item.objectives:
                    alt = self.abreviaText(item.objectives.raw, 400)
                else:
                    alt = self.abreviaText(item.title)
                if len(results) < 4:
                    results.append(dict(title=self.abreviaText(item.title),
                                        alt=alt,
                                        url=item.absolute_url(),
                                        start=item.startplanned,
                                        end=item.startactual,
                                        country=item.country,
                                        location=item.location,
                                        project_manager=item.project_manager,
                                        image=image
                                        ))
        else:
            projects = catalog.unrestrictedSearchResults(
                portal_type='Project',
                context=self.context)
            # Tuple to list in the next code
        
            # Water Operator
            userPartners = api.user.get_current().getProperty('wop_partners')

            userWOPProgram = api.user.get_current().getProperty('wop_programs')

            userRegionalWOPlatform = api.user.get_current().getProperty('wop_platforms')
            if userPartners or userWOPProgram or userRegionalWOPlatform:
                for project in projects:
                    add_project = False
                    item = project._unrestrictedGetObject()
                    if item.wop_program == userWOPProgram:
                        add_project = True
                    if item.wop_platform == userRegionalWOPlatform:
                        add_project = True
                    if item.partners != None:
                        if userPartners in item.partners:
                            add_project = True
                    if add_project:
                        if item.image:
                            image = item.absolute_url() + '/@@images/image/preview'
                        else:
                            image = item.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
                        if item.objectives:
                            alt = self.abreviaText(item.objectives.raw, 400)
                        else:
                            alt = self.abreviaText(item.title)
                        results.append(dict(title=self.abreviaText(item.title),
                                            alt=alt,
                                            url=item.absolute_url(),
                                            start=item.startplanned,
                                            end=item.startactual,
                                            country=item.country,
                                            location=item.location,
                                            project_manager=item.project_manager,
                                            image=image
                                            ))

        return sorted(results, key=itemgetter('title'), reverse=False)

    def allProjects(self):
        # Return random objects 8 if there are more than 8 elements
        # in The site, or 4 if no more than 8
        catalog = api.portal.get_tool('portal_catalog')
        projects = catalog.unrestrictedSearchResults(
            portal_type='Project')
        results = []
        for project in projects:
            item = project._unrestrictedGetObject()
            if item.image:
                image = item.absolute_url() + '/@@images/image/preview'
            else:
                image = item.absolute_url() + '/++theme++gwopa.theme/assets/images/default_image.jpg'
            if item.objectives:
                alt = self.abreviaText(item.objectives.raw, 400)
            else:
                alt = self.abreviaText(item.title)
            results.append(dict(title=self.abreviaText(item.title),
                                alt=alt,
                                url=item.absolute_url(),
                                start=item.startplanned,
                                end=item.startactual,
                                country=item.country,
                                location=item.location,
                                project_manager=item.project_manager,
                                image=image
                                ))
        limit = 8
        items_to_show = 4
        total_results = len(results)

        if total_results >= limit:
            items_to_show = limit
        if total_results < items_to_show:
            items_to_show = len(results)

        return random.sample(results, k=items_to_show)

    def abreviaText(self, text, count=100):
        text = BeautifulSoup(text, 'lxml').text
        if len(text) > count:
            return text[0:count - 10] + '...'
        else:
            return text

    def getBudgetLimits(self):
        items = api.content.find(portal_type="Project")
        values = []
        for item in items:
            value = item.getObject().total_budget
            if value and value != 0:
                values.append(int(value / 100) * 100)
        values.sort()
        if values == []:
            values = [0, 0]
        else:
            values.append(int(values[-1:][0]) + 100)
        return {'start': values[0], 'end': values[-1:][0]}
