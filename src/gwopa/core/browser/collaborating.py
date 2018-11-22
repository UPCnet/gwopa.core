# -*- coding: utf-8 -*-
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone import api


class collaboratingView(BrowserView):
    """ Shows all the collaborating options associated to one project
    """
    __call__ = ViewPageTemplateFile('templates/collaborating.pt')

    def getTitle(self):
        return self.context.Title()

    def getAreas(self):
        items = api.content.find(portal_type='ImprovementArea')
        results = []
        for project in items:
            item = project.getObject()
            if item.image:
                image = True
            else:
                image = False
            if item.description:
                description = item.description
            else:
                description = item.title
            results.append(dict(title=item.title,
                                url=item.absolute_url_path(),
                                image=image,
                                description=description
                                ))
        return results
