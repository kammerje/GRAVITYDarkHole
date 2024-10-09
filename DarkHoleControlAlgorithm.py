from __future__ import division

import os
import pdb
import sys

import astropy.io.fits as pyfits
import matplotlib.pyplot as plt
import numpy as np

import css
from css.simpleServer import simpleServer

import matplotlib
matplotlib.rcParams.update({'font.size': 14})


# =============================================================================
# MAIN
# =============================================================================

class DarkHoleControlAlgorithm(simpleServer):

    def __init__(self,
                 name='DarkHoleControlAlgorithm'):

        super().__init__(name)
        commands = ['INIT',
                    'SETMODE',
                    'GETSKY',
                    'GETSCIENCE',
                    'STOP']

    def cbINIT(self):

        self._db_p2vm = []  # FIXME: read P2VM here
        # self._db_dark = []  # FIXME: read default darks here
        self._db_sky = []  # start with empty cache
        self._db_science = []  # start with empty cache
        self._db_science_fiber_pos = []  # start with empty cache

        self.previous_sky_len = 0
        self.expecting_sky = False
        self.previous_science_len = 0
        self.expecting_science = False

        self.res = None  # undefined upon initialization
        self.axis = None  # undefined upon initialization
        self.pol = None  # undefined upon initialization

        # Distance threshold for fiber pointing above which two objects are no
        # longer considered equal.
        self.dist_threshold = 10.  # mas

        return 'DarkHoleControlAlgorithm successfully initialized'

    def clear_database(self):

        self._db_sky = []  # clear cache
        self._db_science = []  # clear cache
        self._db_science_fiber_pos = []  # clear cache

        return 'Cleared database'

    def cbSETMODE(self,
                  ob_params):

        # New initialization.
        if self.res is None and self.axis is None and self.pol is None:
            self.res = ob_params['???']  # spectral resolution
            self.axis = ob_params['???']  # (dual) on or off
            self.pol = ob_params['???']  # combined or split
        else:
            # New mode == old mode, keep database.
            if self.res == ob_params['???'] and self.axis == ob_params['???'] and self.pol == ob_params['???']:
                pass
            # New mode != old mode, clear database.
            else:
                self.res = ob_params['???']  # spectral resolution
                self.axis = ob_params['???']  # (dual) on or off
                self.pol = ob_params['???']  # combined or split
                self.clear_database()

        return 'OB parameters updated'

    def cbGETSKY(self):

        # Next images will be sky.
        self.previous_sky_len = len(self._db_sky)
        self.expecting_sky = True
        self._db_sky += []  # FIXME: read sky frames here

        pass

    def cbGETSCIENCE(self,
                     fiber_pos):

        # Next images will be science.
        self.previous_science_len = len(self._db_science)
        self.expecting_science = True
        self._db_science += []  # FIXME: read science frames here
        self._db_science_fiber_pos += []  # FIXME: read fiber position here

        # Reduce science data.
        # TODO

        # If star, do nothing.
        fiber_dist = np.sqrt(fiber_pos[0]**2 + fiber_pos[1]**2)
        if fiber_dist <= self.dist_threshold:
            pass
        # If planet, check if new planet == old planet.
        else:
            temp = np.array(self._db_science_fiber_pos)
            dist = np.sqrt(temp[:, 0]**2 + temp[:, 1]**2)
            ww_planet = np.where(dist > self.dist_threshold)
            if len(ww_planet[0]) <= 1:
                pass  # there is only 1 planet exposure
            else:
                if np.abs(temp[ww_planet[0][-1], 0] - temp[ww_planet[0][-2], 0]) < self.dist_threshold and np.abs(temp[ww_planet[0][-1], 1] - temp[ww_planet[0][-2], 1]) < self.dist_threshold:
                    pass  # new planet == old planet
                else:
                    # Only keep new planet.
                    del self._db_science[ww_planet[0][:-1]]
                    del self._db_science_fiber_pos[ww_planet[0][:-1]]

            # Compute correction and send to DM.
            # TODO

        pass

    def cbSTOP(self):

        # Stop data acquisition and clear data belonging to aborted OB.
        self.expecting_sky = False
        self._db_sky = self._db_sky[:self.previous_sky_len]
        self.expecting_science = False
        self._db_science = self._db_science[:self.previous_science_len]

        pass
