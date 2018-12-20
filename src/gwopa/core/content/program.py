# -*- coding: utf-8 -*-
from five import grok
from plone.supermodel import model
from zope import schema
from plone.namedfile import field as namedfile
from gwopa.core import _
from gwopa.core import utils
import re

grok.templatedir("templates")

# email re w/o leading '^'
EMAIL_RE = "([0-9a-zA-Z_&.'+-]+!)*[0-9a-zA-Z_&.'+-]+@(([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-z-A-Z])?\.)+[a-zA-Z]{2,}|([0-9]{1,3}\.){3}[0-9]{1,3})$"


class InvalidEmailError(schema.ValidationError):
    __doc__ = u'Please enter a valid e-mail address.'


def isEmail(value):
    if re.match('^' + EMAIL_RE, value):
        return True
    raise InvalidEmailError


class IProgram(model.Schema):
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
        constraint=isEmail
    )


class View(grok.View):
    grok.context(IProgram)
    grok.template('program_view')
