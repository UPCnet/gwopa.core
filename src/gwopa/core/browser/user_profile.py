from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from gwopa.core.utils import get_safe_member_by_id
from zope.publisher.interfaces import IPublishTraverse, NotFound
from zope.interface import implements
from gwopa.core import _


class userProfile(BrowserView):
    """ Returns an user profile ../profile/{username} """

    implements(IPublishTraverse)

    index = ViewPageTemplateFile('templates/user_profile.pt')

    def __init__(self, context, request):
        super(userProfile, self).__init__(context, request)
        self.username = None
        self.portal = api.portal.get()
        self.portal_url = self.portal.absolute_url()

    def __call__(self):
        return self.index()

    def publishTraverse(self, request, name):
        if self.username is None:  # ../profile/username
            self.username = name
            self.user_info = api.user.get(self.username)
            member_info = get_safe_member_by_id(self.user_info.id)
            self.user_fullname = member_info.get('fullname', '')
            self.fullname = self.user_fullname
        else:
            raise NotFound(self, name, request)
        return self

    def user_properties(self):
        member_data = api.user.get(username=self.username)
        profile__properties = [
            _(u'fullname'),
            _(u'email'),
            _(u'twitter_username'),
            _(u'phone'),
            _(u'region'),
            _(u'country'),
            _(u'wop_program'),
            _(u'wop_platform'),
            _(u'partners'),
            _(u'arees_exp')
        ]

        rendered_properties = []
        for prop in profile__properties:
            rendered_properties.append(dict(
                name=_(prop),
                value=member_data.getProperty(prop, '')
            ))
        return rendered_properties
