#!/usr/bin/env python3

###################################################################################################
# (C) 2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany  #
#                                                                                                 #
# This file is part of dastools.                                                                  #
#                                                                                                 #
# dastools is free software: you can redistribute it and/or modify it under the terms of the GNU  #
# General Public License as published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                                                 #
#                                                                                                 #
# dastools is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without   #
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU   #
# General Public License for more details.                                                        #
#                                                                                                 #
# You should have received a copy of the GNU General Public License along with this program. If   #
# not, see https://www.gnu.org/licenses/.                                                         #
###################################################################################################

"""Tests to check that tdms.py is working

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

   :Copyright:
       2019-2021 Helmholtz Centre Potsdam GFZ German Research Centre for Geosciences, Potsdam, Germany
   :License:
       GPLv3
   :Platform:
       Linux

.. moduleauthor:: Javier Quinteros <javier@gfz-potsdam.de>, GEOFON, GFZ Potsdam
"""

import os
from datetime import datetime
from datetime import timedelta
import numpy as np
from obspy import Trace
from obspy import Stream
from obspy import read
from dastools.input.tdms import TDMS
from dastools.input.das import NoData
from dastools.utils import downloadfile

"""Test the functionality of tdms.py

"""

# Files needed to run the tests
files = dict()
files['PDN_1km_UTC_20180905_095503.298.tdms'] = 'https://nextcloud.gfz-potsdam.de/s/ro286WKCxpP6o4b/download/PDN_1km_UTC_20180905_095503.298.tdms'
files['PDN_1km_UTC_20180905_095533.298.tdms'] = 'https://nextcloud.gfz-potsdam.de/s/zyQZ6wNHCBnQt8J/download/PDN_1km_UTC_20180905_095533.298.tdms'
files['PDN_1km_UTC_20180905_095633.298.tdms'] = 'https://nextcloud.gfz-potsdam.de/s/ggGk3EYTQcknoxs/download/PDN_1km_UTC_20180905_095633.298.tdms'

for file, url in files.items():
    if file not in os.listdir('.'):
        downloadfile(file, url)


# TODO We need a test for decimation=5

def testNoDataFound():
    """when no data is found"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 56, 0)
    # Take only 1 second
    ett = stt + timedelta(seconds=1)

    try:
        TDMS('Wrong-Name', directory, chstart=766, starttime=stt, endtime=ett)
        raise Exception('A NoData exception was expected due to a wrong name of the experiment (filename)')
    except NoData:
        pass


def testIterationMetadata():
    """the iteration through the metadata of the experiment"""

    directory = '.'
    t = TDMS('PDN_1km', directory, chstart=766, iterate='M')
    with t:
        for m in t:
            assert isinstance(m, dict)


def testIterationFiles():
    """the iteration through the files of the experiment"""

    directory = '.'
    t = TDMS('PDN_1km', directory, chstart=766, iterate='F')
    with t:
        for f in t:
            assert isinstance(f, dict)
            assert 'dt' in f.keys()
            assert 'dtend' in f.keys()
            assert 'name' in f.keys()


def testStarttimeTooEarly():
    """when starttime is before the start of the data"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 1, 1, 0, 0, 0)
    t = TDMS('PDN_1km', directory, chstart=766, starttime=stt)
    assert t.starttime > stt


def testChannelsTypes():
    """types of the parameters to select channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 56, 0)
    # Take only 1 second
    ett = stt + timedelta(seconds=1)
    try:
        TDMS('PDN_1km', directory, chstart='a', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to chstart not being a Number')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, chstart=700, chstop='a', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to chstop not being a Number or None')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, chstart=700, chstop=705, chstep='a', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to chstep not being a Number')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, channels='1,2', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to channels being a str')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, channels=1, starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to channels being Number')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, channels=list(), starttime=stt, endtime=ett)
        assert list() != []
    except Exception:
        pass


def testNetworkChannelCodes():
    """format of the network and channel code"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 56, 0)
    # Take only 1 second
    ett = stt + timedelta(seconds=1)
    try:
        TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett, networkcode='A')
        raise Exception('A TypeError was expected due to wrong formatted network code')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett, networkcode='AAA')
        raise Exception('A TypeError was expected due to wrong formatted network code')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett, networkcode=1)
        raise Exception('A TypeError was expected due to wrong formatted network code')
    except TypeError:
        pass

    try:
        TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett, channelcode='AA')
        raise Exception('A TypeError was expected due to wrong formatted channel code')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett, channelcode='AAAA')
        raise Exception('A TypeError was expected due to wrong formatted channel code')
    except TypeError:
        pass
    try:
        TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett, channelcode=1)
        raise Exception('A TypeError was expected due to wrong formatted channel code')
    except TypeError:
        pass


def testChstopUndefined():
    """chstop undefined"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 56, 0)
    # Take only 1 second
    ett = stt + timedelta(seconds=1)

    orig = read('./tests/testChstopUndefined.mseed')
    conv = Stream()

    t = TDMS('PDN_1km', directory, chstart=766, starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Merge Traces
    conv.merge()

    assert np.array_equal(orig[0].data, conv[0].data)


def testOneChannel():
    """One record from one channel"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 56, 0)
    # Take only 250 samples
    ett = stt + timedelta(milliseconds=250)

    orig = read('./tests/testOneChannel.mseed')

    t = TDMS('PDN_1km', directory, chstart=100, chstop=100, starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv = Stream([aux])

    # Check the data
    assert np.array_equal(orig[0].data, conv[0].data)

    # Check the first level attributes
    for item in conv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == conv[0].stats[item]

    # check the attributes within 'mseed'
    for item in conv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]


def testOneChannel2():
    """One record from one channel defined by list of channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 56, 0)
    # Take only 250 samples
    ett = stt + timedelta(milliseconds=250)

    orig = read('./tests/testOneChannel.mseed')

    t = TDMS('PDN_1km', directory, channels=[100], starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv = Stream([aux])

    assert np.array_equal(orig[0].data, conv[0].data)


def testTwoFiles():
    """One record from one channel originally split in two files"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 55, 33)
    # Take only 1000 samples
    ett = stt + timedelta(seconds=1)

    orig = read('./tests/testTwoFiles.mseed')

    t = TDMS('PDN_1km', directory, chstart=99, chstop=99, starttime=stt, endtime=ett)
    with t:
        conv = Stream()
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Merge all Traces with same NSLC code
    conv.merge()

    # Check the data
    assert np.array_equal(orig[0].data, conv[0].data)

    # Check the first level attributes
    for item in conv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == conv[0].stats[item]

    # check the attributes within 'mseed'
    for item in conv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]


def testTwoChannels():
    """One record from two channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 55, 10)
    # Take only 250 samples
    ett = stt + timedelta(milliseconds=250)

    orig = read('./tests/testTwoChannels.mseed')

    t = TDMS('PDN_1km', directory, chstart=100, chstop=101, starttime=stt, endtime=ett)
    with t:
        conv = Stream()
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Check the data
    assert np.array_equal(orig[0].data, conv[0].data)
    assert np.array_equal(orig[1].data, conv[1].data)

    # Check the first level attributes
    for item in conv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == conv[0].stats[item]
            assert orig[1].stats[item] == conv[1].stats[item]

    # check the attributes within 'mseed'
    for item in conv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]
            assert orig[1].stats['mseed'][item] == conv[1].stats['mseed'][item]


def testTwoChannels2():
    """One record from two channels defined by list of channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 55, 10)
    # Take only 250 samples
    ett = stt + timedelta(milliseconds=250)

    orig = read('./tests/testTwoChannels.mseed')

    t = TDMS('PDN_1km', directory, channels=[100, 101], starttime=stt, endtime=ett)
    with t:
        conv = Stream()
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Check the data
    assert np.array_equal(orig[0].data, conv[0].data)
    assert np.array_equal(orig[1].data, conv[1].data)

    # Check the first level attributes
    for item in conv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == conv[0].stats[item]
            assert orig[1].stats[item] == conv[1].stats[item]

    # check the attributes within 'mseed'
    for item in conv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]
            assert orig[1].stats['mseed'][item] == conv[1].stats['mseed'][item]


def testTwoRecords():
    """Two records from one channel"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2018, 9, 5, 9, 55, 10)
    # Take only 4000 samples
    ett = stt + timedelta(seconds=4)

    orig = read('./tests/testTwoRecords.mseed')

    t = TDMS('PDN_1km', directory, chstart=100, chstop=100, starttime=stt, endtime=ett)
    with t:
        conv = Stream()
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Merge all Traces with same NSLC code
    conv.merge()

    # Check the data
    assert np.array_equal(orig[0].data, conv[0].data)

    # Check the first level attributes
    for item in conv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == conv[0].stats[item]

    # check the attributes within 'mseed'
    for item in conv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]
