# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import gwopa.core


class GwopaCoreLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=gwopa.core)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'gwopa.core:default')


GWOPA_CORE_FIXTURE = GwopaCoreLayer()


GWOPA_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(GWOPA_CORE_FIXTURE,),
    name='GwopaCoreLayer:IntegrationTesting',
)


GWOPA_CORE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(GWOPA_CORE_FIXTURE,),
    name='GwopaCoreLayer:FunctionalTesting',
)


GWOPA_CORE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        GWOPA_CORE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='GwopaCoreLayer:AcceptanceTesting',
)
