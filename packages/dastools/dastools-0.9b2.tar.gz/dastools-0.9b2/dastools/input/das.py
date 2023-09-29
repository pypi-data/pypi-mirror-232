"""Das module from dastools.

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

from abc import ABCMeta
from abc import abstractmethod
import datetime


class PotentialGap(Exception):
    """Exception to signal that a gap has been found"""


class NoData(Exception):
    """Exception to signal that there is no data"""


class Das(metaclass=ABCMeta):
    """Base class for the different DAS data formats we can work with"""

    @abstractmethod
    def __enter__(self):
        """
        Method to be run when entering the 'with this_object:' command
        """

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Method to be run when exiting the 'with this_object:' command
        """

    @abstractmethod
    def __iter__(self):
        """Iterate through data (or metadata) and filter and decimate if requested

        :returns: Data and attributes for the header, or metadata
        :rtype: tuple(numpy.array, obspy.core.trace.Stats) or dict
        """

    @abstractmethod
    def __init__(self, experiment: str, directory: str = '.', chstart: int = 0, chstop: int = None,
                 chstep: int = 1, channels: list = None, starttime: datetime.datetime = None,
                 endtime: datetime.datetime = None, iterate: str = 'D', decimate: int = 1,
                 firfilter: str = 'fir235', networkcode: str = 'XX', channelcode: str = 'FSF',
                 loglevel: str = 'INFO'):
        """Initialize the TDMS object selecting the data, channels and decimation

        :param experiment: Experiment to read and process. Usually the first part of the filenames
        :type experiment: str
        :param directory: Directory where files are located
        :type directory: str
        :param chstart: First channel to select
        :type chstart: int
        :param chstop: Last channel to select
        :type chstop: int
        :param chstep: Step between channels in the selection
        :type chstep: int
        :param channels: Selection of channels to work with (list of integers)
        :type channels: list or NoneType
        :param starttime: Start of the selected time window
        :type starttime: datetime.datetime or NoneType
        :param endtime: End of the selected time window
        :type endtime: datetime.datetime or NoneType
        :param iterate: Select either Data (D) or Metadata (M)
        :type iterate: str
        :param decimate: Factor by which the sampling rate is lowered by decimation
        :type decimate: int
        :param firfilter: Filter to apply in case of decimation (fir235 is the only option)
        :type firfilter: str
        :param networkcode: Network code of the experiment. It has to be two alphanumeric characters
        :type networkcode: str
        :param channelcode: Channel code of the experiment. It has to be three alphanumeric characters
        :type channelcode: str
        :param loglevel: Verbosity in the output
        :type loglevel: str
        :raise TypeError: If chstart, or chstop, or chstep are not int. If channels is not a list, or networkcode is
        not a 2 characters code, or channelcode is not a 3 characters code.
        :raise Exception: If channels is empty.
        :raise NoData: If there is no more data available
        """

    @abstractmethod
    def reset(self):
        """Reset the status of the object and start the read again

        :raise IndexError: If the last file has already been processed or the start is greater than end
        """

    @abstractmethod
    def __iter_metadata__(self) -> dict:
        """Read metadata from files based on channel selection

        :return: Metadata from selected channels
        :rtype: dict
        """

    @abstractmethod
    def __iter_data__(self):
        """Read data from files based on channel selection

        :return: Data and attributes for the header
        :rtype: tuple(numpy.array, obspy.core.trace.Stats)
        """

    @abstractmethod
    def __iter_files__(self):
        """List files and basic properties based on selection

        :return: Properties of files
        :rtype: dict
        """

    # @abstractmethod
    # def chunks(self) -> int:
    #     """Estimate number of chunks to iterate"""
    #     pass
