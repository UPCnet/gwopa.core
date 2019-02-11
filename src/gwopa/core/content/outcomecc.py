# -*- coding: utf-8 -*-
import datetime
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.directives import form
from plone import api
from itertools import groupby
from operator import itemgetter

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


class IOutcomecc(model.Schema):
    """  OutcomeCC
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )


class View(grok.View):
    grok.context(IOutcomecc)
    grok.template('outcomecc_view')

    def getItems(self):
        items = api.content.find(
            portal_type='OutcomeCCValues',
            path={'query': '/'.join(self.context.getPhysicalPath()),
                  'depth': 1})
        results = []

        for item in items:
            icon = api.content.find(portal_type='OutcomeCCItem', Title=item.Title)[0].getObject().icon
            category = api.content.find(portal_type='OutcomeCCItem', Title=item.Title)[0].getObject().category
            results.append(dict(
                title=item.Title,
                icon=icon,
                category=category,
                url=item.getURL()))
        return results


class Edit(form.SchemaEditForm):
    grok.context(IOutcomecc)
