"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Jan 9, 2012.
"""
from zope.interface import Interface # pylint: disable=F0401

__docformat__ = 'reStructuredText en'
__all__ = ['ICustomer',
           'IIncidence',
           'IProject',
           'ISite',
           'ISpecies',
           ]


# no __init__ pylint: disable=W0232
class ICustomer(Interface):
    pass


class IProject(Interface):
    pass


class ISpecies(Interface):
    pass


class ISite(Interface):
    pass


class IIncidence(Interface):
    pass
# pylint: enable=W0232
