from zope.interface import implements
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.browser.interfaces import IMainTemplate
from plone import api


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
        if 'Manager' in api.user.get_roles(username=currentuser):
            return True
        else:
            return False

    def myProjects(self):
        catalog = api.portal.get_tool('portal_catalog')
        currentuser = api.user.get_current().id
        results = []
        limit = 1
        if 'Manager' in api.user.get_roles(username=currentuser):
            projects = catalog.unrestrictedSearchResults(
                portal_type='Project',
                context=self.context,
                sort_order='reverse',
                sort_on='modified',
                sort_limit=limit,
                review_state='published')
            for project in projects:
                item = project._unrestrictedGetObject()
                if item.image:
                    image = item.absolute_url_path() + '/@@images/image/preview'
                else:
                    image = item.absolute_url_path() + '/++theme++gwopa.theme/assets/images/128x85.jpg'
                results.append(dict(title=self.abreviaText(item.title),
                                    url=item.absolute_url_path(),
                                    start=item.start,
                                    end=item.end,
                                    country=item.country,
                                    project_manager=item.project_manager,
                                    image=image
                                    ))
        else:
            limit = 4
            projects = catalog.unrestrictedSearchResults(
                portal_type='Project',
                context=self.context,
                sort_order='reverse',
                sort_on='modified',
                sort_limit=limit,
                review_state='published')
            for project in projects:
                item = project._unrestrictedGetObject()
                if item.members:
                    if currentuser in item.members:
                        if item.image:
                            image = item.absolute_url_path() + '/@@images/image/preview'
                        else:
                            image = item.absolute_url_path() + '/++theme++gwopa.theme/assets/images/128x85.jpg'
                        results.append(dict(title=self.abreviaText(item.title),
                                            url=item.absolute_url_path(),
                                            start=item.start,
                                            end=item.end,
                                            country=item.country,
                                            project_manager=item.project_manager,
                                            image=image
                                            ))
        return results

    def companyProjects(self):
        catalog = api.portal.get_tool('portal_catalog')
        projects = catalog.unrestrictedSearchResults(
            portal_type='Project',
            context=self.context,
            review_state='published')
        results = []
        # Manager views all projects
        if 'Manager' in api.user.get_roles(username=api.user.get_current().id):
            for project in projects:
                item = project._unrestrictedGetObject()
                if item.image:
                    image = item.absolute_url_path() + '/@@images/image/preview'
                else:
                    image = item.absolute_url_path() + '/++theme++gwopa.theme/assets/images/128x85.jpg'
                if len(results) < 4:
                    results.append(dict(title=self.abreviaText(item.title),
                                        url=item.absolute_url_path(),
                                        start=item.start,
                                        end=item.end,
                                        country=item.country,
                                        project_manager=item.project_manager,
                                        image=image
                                        ))
                else:
                    return results
        else:
            # Tuple to list in the next code
            userPartners = (list(api.user.get_current().getProperty('wop_partners')))
            for project in projects:
                item = project._unrestrictedGetObject()
                for a in userPartners:
                    if a in item.partners:
                        if item.image:
                            image = item.absolute_url_path() + '/@@images/image/preview'
                        else:
                            image = item.absolute_url_path() + '/++theme++gwopa.theme/assets/images/128x85.jpg'
                        if len(results) < 4:
                            results.append(dict(title=self.abreviaText(item.title),
                                                url=item.absolute_url_path(),
                                                start=item.start,
                                                end=item.end,
                                                country=item.country,
                                                project_manager=item.project_manager,
                                                image=image
                                                ))
                        else:
                            return results
        return results

    def allProjects(self):
        catalog = api.portal.get_tool('portal_catalog')
        projects = catalog.unrestrictedSearchResults(
            portal_type='Project',
            review_state='published')
        results = []
        for project in projects:
            item = project._unrestrictedGetObject()
            if item.image:
                image = item.absolute_url_path() + '/@@images/image/preview'
            else:
                image = item.absolute_url_path() + '/++theme++gwopa.theme/assets/images/128x85.jpg'
            results.append(dict(title=self.abreviaText(item.title),
                                url=item.absolute_url_path(),
                                start=item.start,
                                end=item.end,
                                country=item.country,
                                project_manager=item.project_manager,
                                image=image
                                ))
        return results

    def abreviaText(self, text):
        if len(text) > 100:
            return text[0:90] + '...'
        else:
            return text
