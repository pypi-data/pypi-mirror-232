#! /usr/bin/python
# -*- coding: utf-8 -*-
"""Surrogate Modelling Library for Researchers and Engineers."""

MAJOR = 0
MINOR = 0
PATCH = 1
PRE_RELEASE = '-test'
# Use the following formatting: (major, minor, patch, prerelease)
VERSION = (MAJOR, MINOR, PATCH, PRE_RELEASE)

__shortversion__ = '.'.join(map(str, VERSION[:3]))
__version__ = '.'.join(map(str, VERSION[:3])) + ''.join(VERSION[3:])

__package_name__ = 'surkit'
__contact_names__ = 'EasySurrogate Contributors'
# __contact_emails__ = ''
# __homepage__ = ''
# __repository_url__ = ''
# __download_url__ = ''
# __description__ = ''
__license__ = 'LGPL-3.0'
# __keywords__ = ''
