# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from gwopa.core.testing import GWOPA_CORE_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that gwopa.core is properly installed."""

    layer = GWOPA_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if gwopa.core is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'gwopa.core'))

    def test_browserlayer(self):
        """Test that IGwopaCoreLayer is registered."""
        from gwopa.core.interfaces import (
            IGwopaCoreLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IGwopaCoreLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = GWOPA_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['gwopa.core'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if gwopa.core is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'gwopa.core'))

    def test_browserlayer_removed(self):
        """Test that IGwopaCoreLayer is removed."""
        from gwopa.core.interfaces import \
            IGwopaCoreLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IGwopaCoreLayer,
            utils.registered_layers())
