# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_encode
from Products.statusmessages.interfaces import IStatusMessage

from binascii import b2a_qp
from five import grok
from plone import api
from plone.directives import form

from gwopa.core import _
from gwopa.core.interfaces import IGwopaCoreLayer

import ast
import logging
import transaction

logger = logging.getLogger('gwopa.core')


class ImportMassiveUsers(form.SchemaForm):
    """ New Massive users upload function """
    grok.name('massive-users')
    grok.context(IPloneSiteRoot)
    grok.require('cmf.AddPortalMember')
    grok.layer(IGwopaCoreLayer)

    def __call__(self):
        messages = IStatusMessage(self.request)
        if self.request.method == 'POST':
            if self.request.form['file']:
                try:
                    file = ast.literal_eval(self.request.form['file'])
                    for userdata in file:

                        if not api.user.get(userdata[2]):
                            if userdata[5] == 'Español':
                                language = u'es'
                            elif userdata[5] == 'Français':
                                language = u'fr'
                            else:
                                language = u'en'

                            data = {
                                'fullname': userdata[0].decode('utf-8'),
                                'mail_me': userdata[4],
                                'language': language,
                                'phone': userdata[6].decode('utf-8'),
                                'country': userdata[7].decode('utf-8'),
                                'position': userdata[8].decode('utf-8'),
                                'type_of_organization': userdata[9].decode('utf-8'),
                                'wop_programs': b2a_qp(safe_encode(userdata[10])),
                                'wop_platforms': b2a_qp(safe_encode(userdata[11])),
                                'wop_partners': userdata[12],
                                'common_working_areas': [],  # userdata[13]
                                'donor': userdata[14].decode('utf-8'),
                                'other': userdata[15].decode('utf-8')
                            }

                            api.user.create(
                                username=userdata[2].decode('utf-8'),
                                email=userdata[1].decode('utf-8'),
                                password=userdata[3].decode('utf-8'),
                                properties=data,
                            )

                            # Save user properties
                            transaction.commit()

                    return self.request.response.redirect(self.context.absolute_url() + '/managePortal')
                except SyntaxError:
                    messages.add(_(u"Error datos no validos. Puede comprobar el error en https://codebeautify.org/python-formatter-beautifier"), type=_(u"error"))
                    return self.request.response.redirect(self.context.absolute_url() + '/managePortal')
                except:
                    messages.add(_(u"Error desconocido."), type=_(u"error"))
                    return self.request.response.redirect(self.context.absolute_url() + '/managePortal')
            else:
                messages.add(_(u"Error datos no insertados."), type=_(u"error"))
                return self.request.response.redirect(self.context.absolute_url() + '/managePortal')
        else:
            # Trying to acces this view from another place... redirect!
            return self.request.response.redirect(self.context.absolute_url() + '/managePortal')
