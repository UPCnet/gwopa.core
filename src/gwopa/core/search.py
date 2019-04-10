# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserView
from plone import api


class Search(BrowserView):

    def __call__(self):
        search = api.content.get('/projects').absolute_url()
        searchable_text = self.request.form.get('SearchableText', None)
        query = ''
        if searchable_text:
            query = '#c4={}'.format(searchable_text)
        self.request.response.redirect(search + query)
