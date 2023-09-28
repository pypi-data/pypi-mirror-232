#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""dastools helper functions and utilities

This file is part of dastools.

dastools is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

dastools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If
not, see https://www.gnu.org/licenses/.

   :Copyright:
       2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
   :License:
       GPLv3
   :Platform:
       Linux

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GEOFON, GFZ Potsdam
"""

import datetime
from typing import Union
import pprint
import urllib.request as ul
from obspy.core.trace import Stats


def downloadfile(filename, url):
    """Download a file from the URL passed as parameter

    :param filename: Name of the file to download
    :type filename: str
    :param url: URL where the file is located
    :type url: str
    """
    req = ul.Request(url)

    u = ul.urlopen(req, timeout=15)
    with open(filename, 'wb') as fout:
        fout.write(u.read())


def printmetadata(data):
    """Print the data in a pretty format

    Take into account the special case of a dictionary.
    """
    if isinstance(data, dict):
        pprint.pprint(data)
    else:
        print(data)


def nslc(dataheader: Union[dict, Stats]) -> str:
    """Get a NSLC code from a dictionary with its components

    :param dataheader: Dictionary with components of a NSLC code
    :type dataheader: dict
    :return: NSLC code
    :rtype: str
    :raise KeyError: if keys 'network', 'station', 'location', or 'channel' are not present
    """
    return '%s.%s.%s.%s' % (dataheader['network'].upper(), dataheader['station'].upper(),
                            dataheader['location'].upper(), dataheader['channel'].upper())


def str2date(dstr: str) -> Union[datetime.datetime, None]:
    """Transform a string to a datetime

    :param dstr: A datetime in ISO format.
    :type dstr: str
    :return: A datetime represented the converted input.
    :rtype: datetime.datetime
    :raise ValueError: if no integers are found as components of the string
    """
    # In case of empty string
    if (dstr is None) or (not len(dstr)):
        return None

    dateparts = dstr.replace('-', ' ').replace('T', ' ')
    dateparts = dateparts.replace(':', ' ').replace('.', ' ')
    dateparts = dateparts.replace('Z', '').split()
    # Consider the case in which just the first digits of microseconds
    # are given and complete with 0's to have 6 digits
    if len(dateparts) == 7:
        dateparts[6] = dateparts[6] + '0' * (6 - len(dateparts[6]))

    return datetime.datetime(*map(int, dateparts))
