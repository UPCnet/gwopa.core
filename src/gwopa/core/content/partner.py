# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from plone.namedfile import field as namedfile
from plone import api
from gwopa.core import _
from gwopa.core import utils
from collective.geolocationbehavior.geolocation import IGeolocatable

grok.templatedir("templates")


class IPartner(model.Schema):
    """  Project type
    """
    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u'Summary'),
        required=False,
        missing_value=u'',
    )

    image = namedfile.NamedBlobImage(
        title=_(u'Image'),
        required=False,
    )

    country = schema.List(
        title=_(u"Country"),
        description=_(u"Choose countries from list that represents this country."),
        value_type=schema.Choice(
            source=utils.countries),
        required=True,
    )

    contact = schema.TextLine(
        title=_(u'Contact email'),
        required=False,
        missing_value=u'',
    )


class View(grok.View):
    grok.context(IPartner)
    grok.template('partner_view')

    def usersinthisPartner(self):
        members = api.user.get_users()
        results = []

        for item in members:
            partners = item.getProperty('wop_partners')
            contextpartner = self.context.Title()
            for obj in partners:
                if obj == contextpartner:
                    results += [{'id': item.id,
                                'profile': api.portal.get().absolute_url() + '/profile/' + item.id}]
        return results

    def google_maps_link(self):
        geo = IGeolocatable(self.context, None)
        if geo:
            coordinates = [geo.geolocation.latitude, geo.geolocation.longitude]

            maps_link = "https://www.google.com/maps/place/{0}+{1}/@{0},{1},17z".format(  # noqa
                coordinates[0],
                coordinates[1]
            )
            return maps_link
        else:
            return None
