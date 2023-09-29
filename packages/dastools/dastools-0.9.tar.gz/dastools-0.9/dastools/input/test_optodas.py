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

"""Tests to check that optodas.py is working

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
from dastools.input.das import NoData
from obspy import Trace
from obspy import Stream
from obspy import read
from dastools.input.optodas import OptoDAS
from dastools.utils import downloadfile

"""Test the functionality of optodas.py

"""


# Files needed to run the tests (v7)
files = dict()
files['092853.hdf5'] = {'link': 'https://nextcloud.gfz-potsdam.de/s/jW7t85d53ntNNWe/download/092853.hdf5',
                        'dir': './SineWave/20220110/dphi'}
# Files needed to run the tests (v8)
files['075550.hdf5'] = {'link': 'https://nextcloud.gfz-potsdam.de/s/9cbKTw59ZHSPxCs/download/075550.hdf5',
                        'dir': './example/20220422/dphi'}

for file, urldir in files.items():
    os.makedirs(urldir['dir'], exist_ok=True)
    if file not in os.listdir(urldir['dir']):
        downloadfile(os.path.join(urldir['dir'], file), urldir['link'])


# TODO We need a test for decimation=5

def testConversionv8():
    """Conversion of a stream in v8 format"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 4, 22, 7, 55, 51)
    # Take 7 seconds
    ett = stt + timedelta(seconds=7)

    orig = read('./tests/testConversion-OptoDASv8.mseed')

    t = OptoDAS('example', directory, chstart=4400, chstop=4400, starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv = Stream([aux])

    # Save in BigEndian
    conv.write('deleteme.mseed', format='MSEED', byteorder='>')
    stconv = read('deleteme.mseed')
    os.remove('deleteme.mseed')

    # Check the data
    assert np.array_equal(orig[0].data, stconv[0].data)

    # Check the first level attributes
    for item in stconv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == stconv[0].stats[item]

    # check the attributes within 'mseed'
    for item in stconv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == stconv[0].stats['mseed'][item]


def testNoDataFound():
    """when no data is found"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 1 second
    ett = stt + timedelta(seconds=1)

    try:
        OptoDAS('Wrong-Name', directory, chstart=5597, starttime=stt, endtime=ett)
        raise Exception('A NoData exception was expected due to a wrong name of the experiment (filename)')
    except NoData:
        pass


def testIterationMetadata():
    """the iteration through the metadata of the experiment"""

    directory = '.'
    t = OptoDAS('SineWave', directory, chstart=5597, iterate='M')
    with t:
        for m in t:
            assert isinstance(m, dict)
            assert isinstance(list(m.keys())[0], str)


def testIterationFiles():
    """the iteration through the files of the experiment"""

    directory = '.'
    t = OptoDAS('SineWave', directory, chstart=5597, iterate='F')
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
    stt = datetime(2022, 1, 1, 0, 0, 0)
    t = OptoDAS('SineWave', directory, chstart=5597, starttime=stt)
    assert t.starttime > stt


def testChannelsTypes():
    """types of the parameters to select channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 0.1 second
    ett = stt + timedelta(milliseconds=100)
    try:
        OptoDAS('SineWave', directory, chstart='a', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to chstart not being a Number')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, chstart=5597, chstop='a', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to chstop not being a Number or None')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, chstart=5590, chstop=5595, chstep='a', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to chstep not being a Number')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, channels='1,2', starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to channels being a str')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, channels=1, starttime=stt, endtime=ett)
        raise Exception('A TypeError was expected due to channels being Number')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, channels=list(), starttime=stt, endtime=ett)
        assert list() != []
    except Exception:
        pass


def testNetworkChannelCodes():
    """format of the network and channel code"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 0.1 second
    ett = stt + timedelta(milliseconds=100)
    try:
        OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett, networkcode='A')
        raise Exception('A TypeError was expected due to wrong formatted network code')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett, networkcode='AAA')
        raise Exception('A TypeError was expected due to wrong formatted network code')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett, networkcode=1)
        raise Exception('A TypeError was expected due to wrong formatted network code')
    except TypeError:
        pass

    try:
        OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett, channelcode='AA')
        raise Exception('A TypeError was expected due to wrong formatted channel code')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett, channelcode='AAAA')
        raise Exception('A TypeError was expected due to wrong formatted channel code')
    except TypeError:
        pass
    try:
        OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett, channelcode=1)
        raise Exception('A TypeError was expected due to wrong formatted channel code')
    except TypeError:
        pass


def testChstopUndefined():
    """chstop undefined"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 0.1 second
    ett = stt + timedelta(milliseconds=100)

    orig = read('./tests/testChstopUndefined-OptoDAS.mseed')
    conv = Stream()

    t = OptoDAS('SineWave', directory, chstart=5597, starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Merge Traces
    conv.merge()

    assert len(orig[0].data) == len(conv[0].data)
    # Save in BigEndian
    conv.write('deleteme.mseed', format='MSEED', byteorder='>')
    stconv = read('deleteme.mseed')
    os.remove('deleteme.mseed')
    assert np.array_equal(orig[0].data, stconv[0].data)

    # Check the first level attributes
    for item in stconv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == stconv[0].stats[item]

    # check the attributes within 'mseed'
    for item in stconv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == stconv[0].stats['mseed'][item]


def testOneChannel():
    """One record from one channel"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 250 samples
    ett = stt + timedelta(milliseconds=50)

    orig = read('./tests/testOneChannel-OptoDAS.mseed')

    t = OptoDAS('SineWave', directory, chstart=5000, chstop=5000, starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv = Stream([aux])

    # Save in BigEndian
    conv.write('deleteme.mseed', format='MSEED', byteorder='>')
    stconv = read('deleteme.mseed')
    os.remove('deleteme.mseed')

    # Check the data
    assert np.array_equal(orig[0].data, stconv[0].data)

    # Check the first level attributes
    for item in stconv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == stconv[0].stats[item]

    # check the attributes within 'mseed'
    for item in stconv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == stconv[0].stats['mseed'][item]


def testOneChannel2():
    """One record from one channel defined by list of channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 250 samples
    ett = stt + timedelta(milliseconds=50)

    orig = read('./tests/testOneChannel-OptoDAS.mseed')

    t = OptoDAS('SineWave', directory, channels=[5000], starttime=stt, endtime=ett)
    with t:
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv = Stream([aux])

    # Save in BigEndian
    conv.write('deleteme.mseed', format='MSEED', byteorder='>')
    stconv = read('deleteme.mseed')
    os.remove('deleteme.mseed')

    assert np.array_equal(orig[0].data, stconv[0].data)


# def testTwoFiles():
#     """One record from one channel originally split in two files"""
#
#     directory = '.'
#     # Start of the time window close to the beginning of the file
#     stt = datetime(2018, 9, 5, 9, 55, 33)
#     # Take only 1000 samples
#     ett = stt + timedelta(seconds=1)
#
#     orig = read('./tests/testTwoFiles.mseed')
#
#     t = TDMS('PDN_1km', directory, chstart=99, chstop=99, starttime=stt, endtime=ett)
#     with t:
#         conv = Stream()
#         for data in t:
#             aux = Trace(data=data[0], header=data[1])
#             conv += aux
#
#     # Merge all Traces with same NSLC code
#     conv.merge()
#
#     # Check the data
#     assert np.array_equal(orig[0].data, conv[0].data)
#
#     # Check the first level attributes
#     for item in conv[0].stats:
#         if item != 'mseed':
#             assert orig[0].stats[item] == conv[0].stats[item]
#
#     # check the attributes within 'mseed'
#     for item in conv[0].stats['mseed']:
#         if item != 'blkt1001':
#             assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]


def testTwoChannels():
    """One record from two channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 50 milliseconds
    ett = stt + timedelta(milliseconds=50)

    orig = read('./tests/testTwoChannels-OptoDAS.mseed')

    t = OptoDAS('SineWave', directory, chstart=5000, chstop=5001, starttime=stt, endtime=ett)
    with t:
        conv = Stream()
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Save in BigEndian
    conv.write('deleteme.mseed', format='MSEED', byteorder='>')
    stconv = read('deleteme.mseed')
    os.remove('deleteme.mseed')

    # Check the data
    assert np.array_equal(orig[0].data, stconv[0].data)
    assert np.array_equal(orig[1].data, stconv[1].data)

    # Check the first level attributes
    for item in stconv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == stconv[0].stats[item]
            assert orig[1].stats[item] == stconv[1].stats[item]

    # check the attributes within 'mseed'
    for item in stconv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == stconv[0].stats['mseed'][item]
            assert orig[1].stats['mseed'][item] == stconv[1].stats['mseed'][item]


def testTwoChannels2():
    """One record from two channels defined by list of channels"""

    directory = '.'
    # Start of the time window close to the beginning of the file
    stt = datetime(2022, 1, 10, 9, 29, 0)
    # Take only 50 milliseconds
    ett = stt + timedelta(milliseconds=50)

    orig = read('./tests/testTwoChannels-OptoDAS.mseed')

    t = OptoDAS('SineWave', directory, channels=[5000, 5001], starttime=stt, endtime=ett)
    with t:
        conv = Stream()
        for data in t:
            aux = Trace(data=data[0], header=data[1])
            conv += aux

    # Save in BigEndian
    conv.write('deleteme.mseed', format='MSEED', byteorder='>')
    stconv = read('deleteme.mseed')
    os.remove('deleteme.mseed')

    # Check the data
    assert np.array_equal(orig[0].data, stconv[0].data)
    assert np.array_equal(orig[1].data, stconv[1].data)

    # Check the first level attributes
    for item in stconv[0].stats:
        if item != 'mseed':
            assert orig[0].stats[item] == stconv[0].stats[item]
            assert orig[1].stats[item] == stconv[1].stats[item]

    # check the attributes within 'mseed'
    for item in stconv[0].stats['mseed']:
        if item != 'blkt1001':
            assert orig[0].stats['mseed'][item] == stconv[0].stats['mseed'][item]
            assert orig[1].stats['mseed'][item] == stconv[1].stats['mseed'][item]


# def testTwoRecords():
#     """Two records from one channel"""
#
#     directory = '.'
#     # Start of the time window close to the beginning of the file
#     stt = datetime(2022, 1, 10, 9, 29, 0)
#     # Take only 4000 samples
#     ett = stt + timedelta(seconds=4)
#
#     orig = read('./tests/testTwoRecords-OptoDAS.mseed')
#
#     t = OptoDAS('SineWave', directory, chstart=5200, chstop=5200, starttime=stt, endtime=ett)
#     with t:
#         conv = Stream()
#         for data in t:
#             aux = Trace(data=data[0], header=data[1])
#             conv += aux
#
#     # Merge all Traces with same NSLC code
#     conv.merge()
#
#     # Check the data
#     assert np.array_equal(orig[0].data, conv[0].data)
#
#     # Check the first level attributes
#     for item in conv[0].stats:
#         if item != 'mseed':
#             assert orig[0].stats[item] == conv[0].stats[item]
#
#     # check the attributes within 'mseed'
#     for item in conv[0].stats['mseed']:
#         if item != 'blkt1001':
#             assert orig[0].stats['mseed'][item] == conv[0].stats['mseed'][item]
