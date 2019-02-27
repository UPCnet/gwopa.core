# -*- coding: utf-8 -*-
import datetime
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
from plone.directives import form
from plone import api
from collections import defaultdict

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
    grok.require('zope2.View')

    def getItems(self):

        items = api.content.find(
            portal_type='OutcomeCCValues',
            path={'query': '/'.join(self.context.getPhysicalPath()),
                  'depth': 1})
        results = []
        for item in items:
            outcome = api.content.find(portal_type='OutcomeCCItem', id=item.id)[0].getObject()
            icon = outcome.icon
            category = outcome.category
            results.append(dict(
                title=item.Title,
                icon=icon,
                category=category,
                url=item.getURL()))
        groups = defaultdict(list)
        for obj in results:
            groups[obj['category']].append(obj)

        new_list = groups.values()
        return dict(zero=new_list[0], uno=new_list[1], dos=new_list[2])


class Edit(form.SchemaEditForm):
    grok.context(IOutcomecc)
