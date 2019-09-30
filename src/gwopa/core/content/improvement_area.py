# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from five import grok
from plone import api
from plone.app.event.base import construct_calendar
from plone.app.event.base import first_weekday
from plone.app.event.base import localized_today
from plone.app.event.base import wkday_to_mon1
from plone.app.event.portlets import get_calendar_url
from plone.autoform import directives
from plone.directives import form
from plone.indexer import indexer
from plone.namedfile import field as namedfile
from zope import schema
from zope.i18nmessageid import MessageFactory

from gwopa.core import _
from gwopa.core import utils

import calendar

PLMF = MessageFactory('plonelocales')


grok.templatedir("templates")


class IImprovementArea(form.Schema):
    """  Improvement Area type
    """
    form.mode(title='input')
    title = schema.Choice(
        title=_(u"Title"),
        source=utils.area_title,
        required=True,
    )

    form.mode(description='input')
    description = schema.Text(
        title=_(u'Description'),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Image'),
        description=_(u"Image used to describe the Area. If no file chosen, a defult one will be used."),
        required=False,
    )

    directives.mode(title_es='hidden')
    title_es = schema.TextLine(
        title=_(u"Title Spanish"),
        required=False,
    )

    directives.mode(title_fr='hidden')
    title_fr = schema.TextLine(
        title=_(u"Title French"),
        required=False,
    )


@indexer(IImprovementArea)
def title_es(context):
    try:
        value = context.title_es.decode("utf-8")
        return value
    except:
        return context.title_es


grok.global_adapter(title_es, name='title_es')


@indexer(IImprovementArea)
def title_fr(context):
    try:
        value = context.title_fr.decode("utf-8")
        return value
    except:
        return context.title_fr


grok.global_adapter(title_fr, name='title_fr')


class Edit(form.SchemaEditForm):
    grok.context(IImprovementArea)


class View(grok.View):
    grok.context(IImprovementArea)
    grok.template('improvementarea_view')
    grok.require('zope2.View')

    def getFiles(self):
        """ Return files of the Area """
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['File'],
            path={'query': '/'.join(self.context.getPhysicalPath()) + '/files',
                  'depth': 1})
        results = []
        lang = api.portal.get_current_language()
        if lang == 'es':
            FORMAT_DATE = '%d/%m/%Y'
        else:
            FORMAT_DATE = '%m/%d/%Y'
        for item in items:
            results += [{'title': item.Title,
                         'portal_type': item.portal_type,
                         'url': item.getURL(),
                         'date': item.modification_date.strftime(FORMAT_DATE)
                         }]
        return results

    def getTopics(self):
        """ Return files of the Area """
        portal_catalog = getToolByName(self, 'portal_catalog')
        items = portal_catalog.unrestrictedSearchResults(
            portal_type=['Topic'],
            path={'query': '/'.join(self.context.getPhysicalPath()) + '/topics',
                  'depth': 1})
        results = []
        for item in items:
            results += [{'title': item.Title,
                         'url': item.getURL(),
                         }]
        return results

    def getMembers(self):
        """ Returns Site Members """
        members = api.user.get_users()
        results = []

        wa = self.context.Title()
        for user in members:
            member_wa = user.getProperty('common_working_areas')
            if wa in member_wa:
                results += [{'id': user.id,
                             'fullname': user.getProperty('fullname'),
                             'email': user.getProperty('email'),
                             'image': utils.getPortrait(self, user.id),
                             }]
        return results

    def update(self):
        context = aq_inner(self.context)

        self.calendar_url = get_calendar_url(context, None)

        self.year, self.month = year, month = self.year_month_display()
        self.prev_year, self.prev_month = prev_year, prev_month = (
            self.get_previous_month(year, month))
        self.next_year, self.next_month = next_year, next_month = (
            self.get_next_month(year, month))
        # TODO: respect current url-query string
        self.prev_query = '?month=%s&year=%s' % (prev_month, prev_year)
        self.next_query = '?month=%s&year=%s' % (next_month, next_year)

        self.cal = calendar.Calendar(first_weekday())
        self._ts = getToolByName(context, 'translation_service')
        self.month_name = PLMF(
            self._ts.month_msgid(month),
            default=self._ts.month_english(month)
        )

        # strftime %w interprets 0 as Sunday unlike the calendar.
        strftime_wkdays = [
            wkday_to_mon1(day) for day in self.cal.iterweekdays()
        ]
        self.weekdays = [
            PLMF(self._ts.day_msgid(day, format='s'),
                 default=self._ts.weekday_english(day, format='a'))
            for day in strftime_wkdays
        ]

    @property
    def cal_data(self):
        """Calendar iterator over weeks and days of the month to display.
        """
        context = aq_inner(self.context)
        today = localized_today(context)
        year, month = self.year_month_display()
        monthdates = [dat for dat in self.cal.itermonthdates(year, month)]
        start = monthdates[0]
        end = monthdates[-1]

        date_range_query = {'query': (start, end), 'range': 'min:max'}
        portal_catalog = getToolByName(self.context, 'portal_catalog')
        events = []
        items = portal_catalog.unrestrictedSearchResults(
            portal_type='Event',
            start=date_range_query)
        for event in items:
            session = event._unrestrictedGetObject()
            events.append(session)
        cal_dict = construct_calendar(events, start=start, end=end)

        # [[day1week1, day2week1, ... day7week1], [day1week2, ...]]
        caldata = [[]]
        for dat in monthdates:
            if len(caldata[-1]) == 7:
                caldata.append([])
            date_events = None
            isodat = dat.isoformat()
            if isodat in cal_dict:
                date_events = cal_dict[isodat]

            caldata[-1].append(
                {'date': dat,
                 'day': dat.day,
                 'month': dat.month,
                 'year': dat.year,
                 'prev_month': dat.month < month,
                 'next_month': dat.month > month,
                 'today':
                    dat.year == today.year and
                    dat.month == today.month and
                    dat.day == today.day,
                 'events': date_events})
        return caldata

    def prev_month(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def next_month(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)

    def year_month_display(self):
        """ Return the year and month to display in the calendar.
        """
        context = aq_inner(self.context)
        request = self.request

        # Try to get year and month from request
        year = request.get('year', None)
        month = request.get('month', None)

        # Or use current date
        today = localized_today(context)
        if not year:
            year = today.year
        if not month:
            month = today.month

        # try to transform to number but fall back to current
        # date if this is ambiguous
        try:
            year, month = int(year), int(month)
        except (TypeError, ValueError):
            year, month = today.year, today.month

        return year, month

    def get_previous_month(self, year, month):
        if month == 0 or month == 1:
            month, year = 12, year - 1
        else:
            month -= 1
        return (year, month)

    def get_next_month(self, year, month):
        if month == 12:
            month, year = 1, year + 1
        else:
            month += 1
        return (year, month)
