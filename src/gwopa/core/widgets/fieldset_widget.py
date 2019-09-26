# -*- coding: utf-8 -*-

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from gwopa.core.widgets.interfaces import IFieldsetWidget

import z3c.form.browser.text
import z3c.form.interfaces
import z3c.form.widget
import zope.interface
import zope.schema.interfaces


class FieldsetWidget(z3c.form.browser.text.TextWidget):
    zope.interface.implementsOnly(IFieldsetWidget)

    klass = u'fieldset-widget'
    input_template = ViewPageTemplateFile('templates/fieldset.pt')

    def render(self):
        if self.mode == z3c.form.interfaces.DISPLAY_MODE:
            return self.input_template(self)
        else:
            return self.input_template(self)


@zope.interface.implementer(z3c.form.interfaces.IFieldWidget)
def FieldsetFieldWidget(field, request):
    return z3c.form.widget.FieldWidget(field, FieldsetWidget(request))
