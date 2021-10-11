# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
# from z3c.form.interfaces import INPUT_MODE
from plone.directives import form
from z3c.form.interfaces import DISPLAY_MODE

from gwopa.core import _

import transaction

grok.templatedir("templates")


class ISettingspage(model.Schema):
    """  Settings Page """

    title = schema.TextLine(
        title=_(u"Title"),
        description=_(u"The system will use the settings id. Change for testing purposes only."),
        required=True,
        default=_(u'settings'),
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        default=_(u'This values are necessary for create elements on the Platform'),
    )

    currency = schema.Text(
        title=_(u"Currency Exchange EN"),
        description=_(u'One per line, string and symbol merged with a dash. Ex: USD-US Dollar-$'),
        required=True,
    )

    currency_es = schema.Text(
        title=_(u"Currency Exchange ES"),
        required=True,
    )

    currency_fr = schema.Text(
        title=_(u"Currency Exchange FR"),
        required=True,
    )

    measuring_unit = schema.Text(
        title=_(u'Measuring unit EN'),
        description=_(u'One unit per line. Ex: liters'),
        required=True,
    )

    measuring_unit_es = schema.Text(
        title=_(u'Measuring unit ES'),
        required=True,
    )

    measuring_unit_fr = schema.Text(
        title=_(u'Measuring unit FR'),
        required=True,
    )

    measuring_frequency = schema.Text(
        title=_(u'Monitoring and reporting frequency EN'),
        description=_(u'A string and the number of notifications per year, separated by comma. One per line. Ex: Annually,1'),
        required=True,
    )

    measuring_frequency_es = schema.Text(
        title=_(u'Monitoring and reporting frequency ES'),
        required=True,
    )

    measuring_frequency_fr = schema.Text(
        title=_(u'Monitoring and reporting frequency FR'),
        required=True,
    )

    degree_changes = schema.Text(
        title=_(u'Degree changes EN'),
        description=_(u'Perceived degree of change'),
        required=True,
    )

    degree_changes_es = schema.Text(
        title=_(u'Degree changes ES'),
        required=True,
    )

    degree_changes_fr = schema.Text(
        title=_(u'Degree changes FR'),
        required=True,
    )

    contributed_project = schema.Text(
        title=_(u'Contributed project EN'),
        description=_(u'Project contribution to the perceived change'),
        required=True,
    )

    contributed_project_es = schema.Text(
        title=_(u'Contributed project ES'),
        required=True,
    )

    contributed_project_fr = schema.Text(
        title=_(u'Contributed project FR'),
        required=True,
    )

    consensus = schema.Text(
        title=_(u'Consensus EN'),
        description=_(u'Perceived change decided by'),
        required=True,
    )

    consensus_es = schema.Text(
        title=_(u'Consensus ES'),
        required=True,
    )

    consensus_fr = schema.Text(
        title=_(u'Consensus FR'),
        required=True,
    )

    partner_roles = schema.Text(
        title=_(u'Partner Roles EN'),
        description=_(u'The roles of the partner'),
        required=True,
    )

    partner_roles_es = schema.Text(
        title=_(u'Partner Roles ES'),
        required=True,
    )

    partner_roles_fr = schema.Text(
        title=_(u'Partner Roles FR'),
        required=True,
    )

    organization_roles = schema.Text(
        title=_(u'Organization Roles EN'),
        description=_(u'The roles of other origanizations'),
        required=True,
    )

    organization_roles_es = schema.Text(
        title=_(u'Organization Roles ES'),
        required=True,
    )

    organization_roles_fr = schema.Text(
        title=_(u'Organization Roles FR'),
        required=True,
    )

    overall_score = schema.Text(
        title=_(u'Overall score EN'),
        description=_(u'Perceived degree of change'),
        required=True,
    )

    overall_score_es = schema.Text(
        title=_(u'Overall score ES'),
        required=True,
    )

    overall_score_fr = schema.Text(
        title=_(u'Overall score FR'),
        required=True,
    )

    currency_dict = schema.Text(title=u'', required=False)
    measuring_unit_dict = schema.Text(title=u'', required=False)
    measuring_frequency_dict = schema.Text(title=u'', required=False)
    degree_changes_dict = schema.Text(title=u'', required=False)
    contributed_project_dict = schema.Text(title=u'', required=False)
    consensus_dict = schema.Text(title=u'', required=False)
    partner_roles_dict = schema.Text(title=u'', required=False)
    organization_roles_dict = schema.Text(title=u'', required=False)
    overall_score_dict = schema.Text(title=u'', required=False)


# class View(grok.View):
#     grok.context(ISettingspage)
#     grok.template('settings_view')
#     grok.require('zope2.View')


class Edit(form.SchemaEditForm):
    grok.context(ISettingspage)

    def updateWidgets(self):
        super(Edit, self).updateWidgets()
        self.widgets["title"].mode = HIDDEN_MODE
        self.widgets["description"].mode = DISPLAY_MODE
        self.widgets["currency_dict"].mode = HIDDEN_MODE
        self.widgets["measuring_unit_dict"].mode = HIDDEN_MODE
        self.widgets["measuring_frequency_dict"].mode = HIDDEN_MODE
        self.widgets["degree_changes_dict"].mode = HIDDEN_MODE
        self.widgets["contributed_project_dict"].mode = HIDDEN_MODE
        self.widgets["consensus_dict"].mode = HIDDEN_MODE
        self.widgets["partner_roles_dict"].mode = HIDDEN_MODE
        self.widgets["organization_roles_dict"].mode = HIDDEN_MODE
        self.widgets["overall_score_dict"].mode = HIDDEN_MODE


@grok.subscribe(ISettingspage, IObjectModifiedEvent)
def settingsModified(content, event):
    updateDictsSetting(content)


def updateDictsSetting(content):
    fields = ['measuring_unit', 'measuring_frequency',
              'degree_changes', 'contributed_project', 'consensus', 'partner_roles',
              'organization_roles', 'overall_score']

    for field in fields:
        values_en = getattr(content, field).split('\n')
        values_es = getattr(content, field + '_es').split('\n')
        values_fr = getattr(content, field + '_fr').split('\n')
        info = {}

        for pos, value in enumerate(values_en):
            info.update({values_en[pos]: {'en': values_en[pos],
                                          'es': values_es[pos],
                                          'fr': values_fr[pos]}})

        setattr(content, field + '_dict', info)

    content.currency_dict = {}
    values_en = content.currency.split('\n')
    values_es = content.currency_es.split('\n')
    values_fr = content.currency_fr.split('\n')
    for pos, value in enumerate(values_en):
        currency_key = values_en[pos].split('-')[0]
        content.currency_dict.update({currency_key: {'en': values_en[pos],
                                                     'es': values_es[pos],
                                                     'fr': values_fr[pos]}})

    content.reindexObject()
    transaction.commit()
