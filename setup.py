# -*- coding: utf-8 -*-
"""Installer for the gwopa.core package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='gwopa.core',
    version='1.8.dev0',
    description="An add-on for Plone",
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Roberto Diaz',
    author_email='plone.team@upcnet.es',
    url='https://pypi.python.org/pypi/gwopa.core',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['gwopa'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
        'plone.api>=1.8.4',
        'plone.restapi',
        'Products.GenericSetup>=1.8.2',
        'plone.app.dexterity [grok]',
        'setuptools',
        'z3c.jbot',
        'pycountry',
        'requests',
        'plone.patternslib',
        'collective.geolocationbehavior',
        'plone.formwidget.geolocation',
        'repoze.catalog',
        'souper',
        'Products.PloneKeywordManager',
        'geojson',
        'collective.ploneboard',
        'eea.facetednavigation',
        'beautifulsoup4',
        'plone.formwidget.autocomplete',
        'collective.dexteritytextindexer'
        # 'ftw.calendarwidget',
        # 'ftw.keywordwidget',
        # 'ftw.datepicker',
        # 'plone.app.workflowmanager'
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]'
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
