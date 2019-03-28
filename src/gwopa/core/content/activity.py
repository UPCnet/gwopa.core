# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from gwopa.core import _
import datetime
from plone.app.z3cform.widget import SelectWidget
from plone.autoform import directives
from plone.directives import form
# from z3c.form.interfaces import IAddForm, IEditForm
# from datetime import date
from plone.app.z3cform.widget import DatetimeFieldWidget
# from z3c.form.interfaces import IFieldWidget
# from z3c.form.widget import FieldWidget
# from zope.interface import implementer

# from zope.formlib.widgets import DateI18nWidget
# from zope.i18n.format import DateTimeParseError
# from zope.app.form.interfaces import ConversionError
from ftw.datepicker.widget import DateTimePickerWidgetFactory

grok.templatedir("templates")


def todayValue():
    return datetime.date.today()


current_year = datetime.date.today().year


class IActivity(model.Schema):
    """  Activity """

    form.widget(due_date=DateTimePickerWidgetFactory)
    due_date = schema.Date(
        title=_(u"Other Date picker only works with no modals"),
    )

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    initial_situation = schema.Text(
        title=_(u'Initial situation description'),
        required=False,
        missing_value=u'',
    )

    start = schema.Date(
        title=_(u'Starting date'),
        required=True,
        defaultFactory=todayValue,
    )

    directives.widget(
        'start',
        DatetimeFieldWidget,
        pattern_options={
            "date": {
                'min': [current_year - 2, 1, 1],
                'max': [current_year + 20, 1, 1],
                'selectYears': 12,
            },
            'time': False,
            'format': 'M/d/yy',
        },
    )

    end = schema.Date(
        title=_(u'Completion date'),
        required=True,
        defaultFactory=todayValue,
    )

    budget = schema.Text(
        title=_(u'Assigned budget'),
        required=False,
        missing_value=u'',
    )

    directives.mode(currency='display')
    currency = schema.Text(
        title=_(u''),
    )

    directives.widget('members', SelectWidget)
    members = schema.List(
        title=_(u"Responsible people"),
        value_type=schema.Choice(
            source=u'plone.app.vocabularies.Users'),
        required=False,
    )


@form.default_value(field=IActivity['currency'])
def projectCurrency(data):
    # return data.context.aq_parent.currency.split('-')[-1].lstrip(' ').rstrip(' ')
    return data.context.aq_parent.currency


class Edit(form.SchemaEditForm):
    grok.context(IActivity)

    def updateWidgets(self):
        # form_fields['start_date'].custom_widget = MyDateI18nWidget
        super(Edit, self).updateWidgets()
        # self.widgets['start'].custom_widget = MyDateI18nWidget
    #     self.widgets['start'].config['selectYears'] = 10


class View(grok.View):
    grok.context(IActivity)
    grok.template('activity_view')
    grok.require('zope2.View')
