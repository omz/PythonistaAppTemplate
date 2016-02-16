
"""Shared OS X support functions."""

import os
import re
import sys

__all__ = [
    'get_platform_osx',
]

_SYSTEM_VERSION = None

def _get_system_version():
    """Return the OS X system version as a string"""
    # Reading this plist is a documented way to get the system
    # version (see the documentation for the Gestalt Manager)
    # We avoid using platform.mac_ver to avoid possible bootstrap issues during
    # the build of Python itself (distutils is used to build standard library
    # extensions).

    global _SYSTEM_VERSION

    if _SYSTEM_VERSION is None:
        _SYSTEM_VERSION = ''
        try:
            f = open('/System/Library/CoreServices/SystemVersion.plist')
        except IOError:
            # We're on a plain darwin box, fall back to the default
            # behaviour.
            pass
        else:
            try:
                m = re.search(r'<key>ProductVersion</key>\s*'
                              r'<string>(.*?)</string>', f.read())
            finally:
                f.close()
            if m is not None:
                _SYSTEM_VERSION = '.'.join(m.group(1).split('.')[:2])
            # else: fall back to the default behaviour

    return _SYSTEM_VERSION

def customize_config_vars(_config_vars):
    return _config_vars

def get_platform_osx(_config_vars, osname, release, machine):
    """Filter values for get_platform()"""
    osname = 'iphoneos'
    release = _get_system_version()
    return (osname, release, machine)
