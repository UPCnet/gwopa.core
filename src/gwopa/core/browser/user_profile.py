from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from gwopa.core.utils import get_safe_member_by_id


class userProfile(BrowserView):
    """ Returns an user profile ../profile/{username} """

    index = ViewPageTemplateFile('templates/user_profile.pt')

    def __init__(self, context, request):
        super(userProfile, self).__init__(context, request)
        self.username = None
        self.portal = api.portal.get()
        self.portal_url = self.portal.absolute_url()

    def __call__(self):
        return self.index()

    def publishTraverse(self, request, name):
            self.username = name
            self.user_info = api.user.get(self.username)
            member_info = get_safe_member_by_id(self.user_info.id)
            self.user_fullname = member_info.get('fullname', '')
            self.fullname = self.user_fullname
            return self

    def user_properties(self):
        member_data = api.user.get_current()
        return {'fullname': member_data.getProperty('fullname'),
                'email': member_data.getProperty('email'),
                'description': member_data.getProperty('description'),
                'twitter_username': member_data.getProperty('twitter_username'),
                'phone': member_data.getProperty('phone'),
                'region': member_data.getProperty('region'),
                }
