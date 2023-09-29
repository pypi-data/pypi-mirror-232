#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""dasmetadata tool

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

import argparse
import os
import sys
import logging
from dastools.input.tdms import TDMS
from dastools.input.optodas import OptoDAS
from dastools import __version__
from dastools.utils import str2date
from dastools.utils import printmetadata


def main():
    dasclasses = ['OptoDAS', 'TDMS']

    # Check verbosity in the output
    msg = 'Read and convert metadata from different DAS formats to standard representations.'
    parser = argparse.ArgumentParser(description=msg)
    parser.add_argument('-l', '--loglevel',
                        help='Verbosity in the output.',
                        choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO',
                                 'DEBUG'],
                        default='INFO')
    parser.add_argument('-d', '--directory',
                        help='Directory where files are located (default: ".")',
                        default='.')
    parser.add_argument('--start', '--starttime',
                        help='Start of the selected time window.\nFormat: 2019-02-01T00:01:02.123456Z',
                        default=None)
    parser.add_argument('--end', '--endtime',
                        help='End of the selected time window.\nFormat: 2019-02-01T00:01:02.123456Z',
                        default=None)
    parser.add_argument('--chstart', type=int,
                        help='First channel to export',
                        default=0)
    parser.add_argument('--chstop', type=int,
                        help='Last channel to export',
                        default=None)
    parser.add_argument('--chstep', type=int,
                        help='Step between channels in the selection',
                        default=1)
    parser.add_argument('-f', '--inputfmt', type=str, choices=dasclasses,
                        help='Format of the input files', default=None)
    parser.add_argument('-V', '--version', action='version', version='dasconv v%s' % __version__)
    parser.add_argument('filename',
                        help='Experiment to read and process. It is usually the first part of the filenames.')

    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel, stream=sys.stdout)

    logs = logging.getLogger('OpenFile')
    logs.setLevel(args.loglevel)

    dtstart = str2date(args.start)
    dtend = str2date(args.end)

    if dtend is not None and dtstart is not None and dtstart >= dtend:
        logs.error('End time is smaller than start time.')
        return

    # If there are no input format try to guess it from the file extension filtering them with the parameters provided
    if args.inputfmt is None:
        # List all files to potentially process
        listfiles = [filename for filename in os.listdir(args.directory) if filename.startswith(args.filename)]
        if not listfiles:
            logs.error('No files found starting with %s' % args.filename)
            sys.exit(-2)
        # Check the extension of the first file
        extension = os.path.splitext(listfiles[0])[1].lower()
        logs.debug('Extension found in files is "%s"' % extension)
        # and guess the input format based on the extension
        if extension.endswith('tdms'):
            inputfmt = 'TDMS'
        elif extension.endswith('hdf5') or extension.endswith('h5'):
            inputfmt = 'OptoDAS'
        else:
            logs.error('Input format cannot be guessed from the files found in the directory')
            sys.exit(-2)
    else:
        inputfmt = args.inputfmt

    if inputfmt == 'TDMS':
        clsdas = TDMS
    elif inputfmt == 'OptoDAS':
        clsdas = OptoDAS
    else:
        logs.error('Unknown input format.')
        sys.exit(-2)

    dasobj = clsdas(args.filename, directory=args.directory, iterate='M', starttime=dtstart, endtime=dtend,
                    chstart=args.chstart, chstop=args.chstop, chstep=args.chstep,
                    loglevel='WARNING')
    # progress = tqdm(dasobj)
    for data in dasobj:  # progress:
        printmetadata(data)
    return


if __name__ == '__main__':
    main()
