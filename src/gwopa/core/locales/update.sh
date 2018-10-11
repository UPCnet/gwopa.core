#!/bin/bash
# i18ndude should be available in current $PATH (eg by running
# ``export PATH=$PATH:$BUILDOUT_DIR/bin`` when i18ndude is located in your buildout's bin directory)
#
# For every language you want to translate into you need a
# locales/[language]/LC_MESSAGES/gwopa.po
# (e.g. locales/de/LC_MESSAGES/gwopa.po)

domain=gwopa

echo ""
echo "### Remember to add MANUALLY the NEW gwopa.theme directories to this script ###"
echo "### This script doesnt check the THEME directory.                           ###"
echo "### Add the missings dir, excluding theme dir.                              ###"
echo ""
../../../../../../bin/i18ndude rebuild-pot --pot $domain.pot --create $domain  ../  \
  ../../../../../gwopa.theme/src/gwopa/theme/behaviors  \
  ../../../../../gwopa.theme/src/gwopa/theme/browser \
  ../../../../../gwopa.theme/src/gwopa/theme/content \
  ../../../../../gwopa.theme/src/gwopa/theme/profiles \
  ../../../../../gwopa.theme/src/gwopa/theme/templates
../../../../../../bin/i18ndude sync --pot $domain.pot */LC_MESSAGES/$domain.po
