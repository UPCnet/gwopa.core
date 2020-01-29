# -*- coding: utf-8 -*-
from five import grok
from plone import api

from gwopa.core.interfaces import IGwopaCoreLayer
from gwopa.core.content.project import IProject

class generateAutomaticReport(grok.View):
    grok.name('generateAutomaticReport')
    grok.context(IProject)
    grok.layer(IGwopaCoreLayer)
    grok.require('cmf.ManagePortal')

    def render(self):
        num_report = self.request.form.get('num_report', False)
        if not num_report:
            return 'KO: Required num_report parameter'

        project_year = self.request.form.get('project_year', False)
        if not project_year:
            return 'KO: Required project_year parameter'

        project = self.context
        if 'reports' in project:
            reports_content = project['reports']
            title = num_report + '-PY' + project_year + '-' + project.code + '-' + project.title.upper()
            report = api.content.create(
                type='Report',
                title=title,
                project_year=project_year,
                report_type='auto',
                container=reports_content)

            # generateReportData(report)

            return 'OK: ' + report.absolute_url()
        else:
            return 'KO: ' + project.absolute_url() + 'don\'t have reports folder'
